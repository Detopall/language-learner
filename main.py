import sqlite3
import secrets
import datetime
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Form, Depends, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from database.db_user_crud import get_user, add_user, verify_user_password
from database.db_session_crud import add_session_token, get_session_token_from_user
from database.db import create_tables, get_db

STATIC_FOLDER = "static"
TEMPLATES_FOLDER = f"{STATIC_FOLDER}/templates"

app = FastAPI()

# Initialize DB tables
init_db = sqlite3.connect("database/database.db")
create_tables(init_db)
init_db.close()

# Mount static files
app.mount(f"/{STATIC_FOLDER}", StaticFiles(directory=STATIC_FOLDER), name=STATIC_FOLDER)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_FOLDER)


@app.get("/")
async def root():
	return FileResponse(f"{STATIC_FOLDER}/index.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
	return templates.TemplateResponse("dashboard.html", {"request": request})


@app.post("/auth", response_class=HTMLResponse)
async def auth(
	request: Request,
	username: str = Form(...),
	password: str = Form(...),
	db: sqlite3.Connection = Depends(get_db),
):
	user = get_user(db, username)
	if not user:
		user = add_user(db, username, password)

	if not verify_user_password(password, user[2]):
		print(verify_user_password(password, user[2]))
		return templates.TemplateResponse(
			"auth_error.html",
			{"request": request, "username": username, "error": "Invalid username or password."},
			status_code=200,
		)

	session_data = get_session_token_from_user(db, username, password)
	if not session_data:
		session_token = secrets.token_hex(16)
		expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=5)
		add_session_token(db, username, session_token, expires_at)
	else:
		session_token = session_data["token"]
		expires_at = session_data["expires_at"]

	response = templates.TemplateResponse("dashboard.html", {"request": request})
	response.set_cookie(
		key="sessionToken",
		value=session_token,
		expires=expires_at,
	)
	return response


if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
