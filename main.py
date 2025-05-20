import sqlite3
import secrets
import datetime
import base64
import subprocess
from io import BytesIO

import uvicorn
from pathlib import Path
from fastapi import FastAPI, Form, Depends, Response, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from PIL import Image

from database.db_user_crud import get_user, add_user, verify_user_password
from database.db_session_crud import add_session_token, get_session_token_from_user
from database.db import create_tables, get_db
from handwriting.handwriting_predict import predict_image

STATIC_FOLDER = "static"
TEMPLATES_FOLDER = f"{STATIC_FOLDER}/templates"

app = FastAPI()

# Initialize DB tables
init_db = sqlite3.connect("database/database.db")
create_tables(init_db)
init_db.close()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="secret")

# Mount static files
app.mount(f"/{STATIC_FOLDER}", StaticFiles(directory=STATIC_FOLDER), name=STATIC_FOLDER)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_FOLDER)

async def get_authenticated_user(request: Request, db: sqlite3.Connection = Depends(get_db)):
	session_token = request.cookies.get("sessionToken")
	print(session_token)

	if not session_token:
		raise HTTPException(status_code=403, detail="Missing session token")

	cur = db.cursor()
	cur.execute("SELECT * FROM sessions WHERE token = ?", (session_token,))
	session = cur.fetchone()

	if not session:
		raise HTTPException(status_code=401, detail="Invalid session token")

	return session[1]


def translate_once(text):
	"""Run trans for a single auto-detected translation and return stripped output."""
	result = subprocess.run(
		["trans", "-b", text],
		capture_output=True,
		text=True,
	)
	return result.stdout.strip()

def auto_translate_until_stable(text, max_iterations=3):
	"""Repeatedly translate until the output stabilizes or max_iterations reached."""
	current = text
	for _ in range(max_iterations):
		result = translate_once(current)
		if result == current:
			return result
		current = result
	return current

def new_character(request):
	character = secrets.choice(open("handwriting/labels_fixed.txt", encoding="utf-8").readlines()).strip()
	explanation = auto_translate_until_stable(character)

	print(f"Character: {character} | Explanation: {explanation}")
	request.session["original_char"] = character
	return character, explanation, request


@app.get("/")
async def root():
	return FileResponse(f"{STATIC_FOLDER}/index.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user_id: int = Depends(get_authenticated_user)):
	return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/writing", response_class=HTMLResponse)
async def writing(request: Request, user_id: int = Depends(get_authenticated_user)):
	character, explanation, request = new_character(request)
	return templates.TemplateResponse("writing.html", {"request": request, "character": character, "explanation": explanation})

@app.get("/writing-reset", response_class=HTMLResponse)
async def writing_reset(request: Request, user_id: int = Depends(get_authenticated_user)):
	character, explanation, request = new_character(request)
	return templates.TemplateResponse("canvas_fragment.html", {"request": request, "character": character, "explanation": explanation})


@app.post("/writing-prediction", response_class=HTMLResponse)
async def writing_prediction(request: Request, user_id: int = Depends(get_authenticated_user)):
	form = await request.form()
	canvas_data = form.get("canvas_data")

	if not canvas_data:
		return HTMLResponse(content="No canvas data received", status_code=400)

	img = Image.open(BytesIO(base64.b64decode(canvas_data)))
	img_path = "handwriting/drawing.png"
	img.save(img_path)

	predicted_char = predict_image(img_path)
	original_char = request.session.get("original_char")

	print(predicted_char == original_char)

	if predicted_char != original_char:
		return templates.TemplateResponse("prediction_result.html", {
			"request": request,
			"prediction": predicted_char,
			"error": f"Try drawing again, the prediction didn't match the original character: {original_char}."
		})
	else:
		return templates.TemplateResponse("prediction_result.html", {
			"request": request,
			"prediction": predicted_char,
			"message": "Correct! The prediction matched the original character."
		})

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
