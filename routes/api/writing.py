import base64
import subprocess
import secrets
from io import BytesIO

from fastapi import FastAPI, Form, Depends, Response, Request, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from PIL import Image

from config import get_templates
from database.db import get_db
from routes.auth import get_authenticated_user
from handwriting.handwriting_predict import predict_image

router = APIRouter()

templates = get_templates()

def translate_once(text: str):
	"""
	Translate text once using Google Translate.

	Args:
		text (str): The text to translate.

	Returns:
		str: The translated text.
	"""
	result = subprocess.run(
		["trans", "-b", text],
		capture_output=True,
		text=True,
	)
	return result.stdout.strip()

def auto_translate_until_stable(text: str, max_iterations=3):
	"""
	Repeatedly translate text until it no longer changes.

	Args:
		text (str): The text to translate.
		max_iterations (int, optional): The maximum number of iterations to run. Defaults to 3.

	Returns:
		str: The translated text.
	"""

	current = text
	for _ in range(max_iterations):
		result = translate_once(current)
		if result == current:
			return result
		current = result
	return current

def new_character(request: Request):
	character = secrets.choice(open("handwriting/labels_fixed.txt", encoding="utf-8").readlines()).strip()
	explanation = auto_translate_until_stable(character)

	print(f"Character: {character} | Explanation: {explanation}")
	request.session["original_char"] = character
	return character, explanation, request


@router.get("", response_class=HTMLResponse)
async def writing(request: Request, user_id: int = Depends(get_authenticated_user)):
	"""
	Display the writing page

	Args:
		request (Request): The request object
		user_id (int, optional): The user ID. Defaults to Depends(get_authenticated_user).

	Returns:
		HTMLResponse: The response object
	"""
	character, explanation, request = new_character(request)
	return templates.TemplateResponse("writing.html", {"request": request, "character": character, "explanation": explanation})

@router.get("/reset", response_class=HTMLResponse)
async def writing_reset(request: Request, user_id: int = Depends(get_authenticated_user)):
	"""
	Display the writing page

	Args:
		request (Request): The request object
		user_id (int, optional): The user ID. Defaults to Depends(get_authenticated_user).

	Returns:
		HTMLResponse: The response object
	"""
	character, explanation, request = new_character(request)
	return templates.TemplateResponse("canvas_fragment.html", {"request": request, "character": character, "explanation": explanation})


@router.post("/prediction", response_class=HTMLResponse)
async def writing_prediction(request: Request, user_id: int = Depends(get_authenticated_user)):
	"""
	Display the writing page

	Args:
		request (Request): The request object
		user_id (int, optional): The user ID. Defaults to Depends(get_authenticated_user).

	Returns:
		HTMLResponse: The response object
	"""

	form = await request.form()
	canvas_data = form.get("canvas_data")

	if not canvas_data:
		return HTMLResponse(content="No canvas data received", status_code=400)

	img = Image.open(BytesIO(base64.b64decode(canvas_data)))
	img_path = "handwriting/drawing.png"
	img.save(img_path)

	predicted_char = predict_image(img_path)
	original_char = request.session.get("original_char")

	if predicted_char != original_char:
		return templates.TemplateResponse("prediction_result.html", {
			"request": request,
			"prediction": predicted_char,
			"error": f"Try drawing again, the prediction didn't match the original character: {original_char}. You might've drawn this: {predicted_char}"
		})
	else:
		return templates.TemplateResponse("prediction_result.html", {
			"request": request,
			"prediction": predicted_char,
			"message": "Correct! The drawing matched the original character."
		})
