import datetime
import secrets
import sqlite3

from fastapi import FastAPI, APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import get_templates
from database.db import get_db
from database.db_user_crud import get_user, add_user, verify_user_password
from database.db_session_crud import get_session_token_from_user, add_session_token

router = APIRouter()

templates = get_templates()

async def get_authenticated_user(request: Request, db: sqlite3.Connection = Depends(get_db)):
	"""
	Get the authenticated user

	Args:
		request (Request): The request object
		db (sqlite3.Connection, optional): The database connection. Defaults to Depends(get_db).

	Returns:
		int: The user ID
	"""
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

@router.post("", response_class=HTMLResponse)
async def auth(
	request: Request,
	username: str = Form(...),
	password: str = Form(...),
	db: sqlite3.Connection = Depends(get_db),
):
	"""
	Authenticate user

	Args:
		request (Request): The request object
		username (str, optional): The username of the user. Defaults to Form(...).
		password (str, optional): The password of the user. Defaults to Form(...).
		db (sqlite3.Connection, optional): The database connection. Defaults to Depends(get_db).

	Returns:
		HTMLResponse: The response object
	"""
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
