import base64
import json
import subprocess
import secrets
import requests
from io import BytesIO

from fastapi import FastAPI, Form, Depends, Response, Request, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import get_templates
from routes.auth import get_authenticated_user
from routes.api.writing import auto_translate_until_stable

router = APIRouter()


def generate_japanese_story(length='short', difficulty='easy'):
	"""
	Generate a Japanese story

	Args:
		length (str, optional): The length of the story. Defaults to 'short'.
		difficulty (str, optional): The difficulty of the story. Defaults to 'easy'.

	Returns:
		title (str): The title of the story.
		story (str): The story itself.
	"""
	url = "http://localhost:11434/api/chat"

	# Length and difficulty instructions in Japanese
	length_map = {
		'short': '50文字程度の短い',
		'medium': '150文字程度の中くらいの',
		'long': '300文字以上の長い'
	}
	difficulty_map = {
		'easy': '簡単な言葉を使って',
		'medium': '少し難しい単語も使って',
		'hard': '難しい語彙や表現を使って'
	}
	length_instruction = length_map.get(length, length_map['short'])
	difficulty_instruction = difficulty_map.get(difficulty, difficulty_map['easy'])

	prompt = str(length_instruction) + " 日本語の物語を書いてください。" + str(difficulty_instruction) + " ください。返答は必ず次のJSON形式で出力してください。 {'title': <物語のタイトル>, 'story': <物語の本文（必ず空ではなく、内容を含めてください）>} タイトルと本文はどちらも日本語（漢字・ひらがな・カタカナ）で書いてください。ローマ字や英語は使わないでください。"

	payload = {
		"model": "llama3",
		"messages": [
			{"role": "user", "content": prompt}
		],
		"stream": False,
		"format": {
			"type": "object",
			"properties": {
				"title": {"type": "string"},
				"story": {"type": "string"}
			},
			"required": ["title", "story"]
		},
		"options": {
			"temperature": 0.7
		}
	}

	headers = {"Content-Type": "application/json"}
	response = requests.post(url, headers=headers, json=payload)
	response.raise_for_status()
	response = response.json()
	print(response)
	content = response["message"]["content"]
	content_dict = json.loads(content)
	return content_dict["title"], content_dict["story"]


@router.get("", response_class=HTMLResponse)
async def reading(request: Request, user_id: int = Depends(get_authenticated_user)):
	"""
	Display the reading page

	Args:
		request (Request): The request object
		user_id (int, optional): The user ID. Defaults to Depends(get_authenticated_user).

	Returns:
		HTMLResponse: The response object
	"""
	templates = get_templates()
	return templates.TemplateResponse("reading.html", {"request": request})

@router.post("", response_class=HTMLResponse)
async def create_story(
	request: Request,
	user_id: int = Depends(get_authenticated_user),
	story_difficulty: str = Form(...),
	story_length: str = Form(...)
):
	"""
	Create a story with up to 3 attempts if the story is not returned.
	"""
	max_tries = 3
	for attempt in range(max_tries):
		title, story = generate_japanese_story(length=story_length, difficulty=story_difficulty)
		if story and story.strip():
			break
	else:
		# If all attempts fail, set a default error message
		title = "エラー"
		story = "ストーリーの生成に失敗しました。もう一度お試しください。"

	request.session["title"] = title
	request.session["story"] = story
	request.session["story_difficulty"] = story_difficulty
	request.session["story_length"] = story_length

	templates = get_templates()
	return templates.TemplateResponse(
		"reading_story.html",
		{
			"request": request,
			"title": title,
			"story": story,
			"story_difficulty": story_difficulty,
			"story_length": story_length,
		}
	)

@router.post("/translate")
async def translate(request: Request, user_id: int = Depends(get_authenticated_user)):
	"""
	Translate the story
	"""

	title = request.session.get("title")
	story = request.session.get("story")
	title_translation, story_translation = auto_translate_until_stable(title), auto_translate_until_stable(story)

	templates = get_templates()
	return templates.TemplateResponse(
		"reading_story.html",
		{
			"request": request,
			"title": title,
			"story": story,
			"story_difficulty": request.session.get("story_difficulty"),
			"story_length": request.session.get("story_length"),
			"title_translation": title_translation,
			"story_translation": story_translation
		}
	)
