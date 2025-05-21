import requests
import json

from fastapi import FastAPI, Form, Depends, Response, Request, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import get_templates
from routes.auth import get_authenticated_user
from routes.api.writing import auto_translate_until_stable


router = APIRouter()

templates = get_templates()

URL = "http://localhost:11434/api/chat"

def get_quiz():
	"""
	Sends a prompt to Ollama to generate a quiz.

	Returns:
		dict: A dictionary containing the question and choices.
	"""

	prompt = (
		"日本語の穴埋め問題を1つ作成してください。返答は必ず次のJSON形式で出力してください。{'question': <空欄を含む日本語の文>, 'choices': [<選択肢1>, <選択肢2>, <選択肢3>, <選択肢4>]} 文、選択肢、正解はすべて日本語（漢字・ひらがな・カタカナ）で書いてください。ローマ字は使わないでください。"
	)

	payload = {
		"model": "llama3",
		"messages": [
			{"role": "user", "content": prompt}
		],
		"stream": False,
		"format": {
			"type": "object",
			"properties": {
				"question": {"type": "string"},
				"choices": {
					"type": "array",
					"items": {"type": "string"}
				}
			},
			"required": ["question", "choices"]
		},
		"options": {
			"temperature": 0.7
		}
	}

	headers = {"Content-Type": "application/json"}
	response = requests.post(URL, headers=headers, json=payload)
	response.raise_for_status()
	response = response.json()
	print(response)
	content = response["message"]["content"]
	content_dict = json.loads(content)
	return content_dict["question"], content_dict["choices"]

def get_correct_answer(question: str, choices: list):
	"""
	Get the correct answer for a given question and choices from Ollama.

	Args:
		question (str): The question.
		choices (list): The choices.

	Returns:
		str: The correct answer.
	"""

	prompt = (
		"Given the question: " + question + " and the choices: " + str(choices) + " which one is the correct answer? Respond with the number of the correct answer, starting from 1. Make sure the response is a number and is in the range of the choices. Do not respond with anything else."
	)

	payload = {
		"model": "llama3",
		"messages": [
			{"role": "user", "content": prompt}
		],
		"stream": False,
		"options": {
			"temperature": 0.7
		}
	}

	headers = {"Content-Type": "application/json"}
	response = requests.post(URL, headers=headers, json=payload)
	response.raise_for_status()
	response = response.json()
	print(response)
	return int(response["message"]["content"])

def auto_generate_quiz_until_stable(max_iterations=3):
	"""
	Repeatedly generate a quiz until it no longer changes.

	Args:
		max_iterations (int, optional): The maximum number of iterations to run. Defaults to 3.

	Returns:
		tuple: A tuple containing the question and choices.
	"""
	question, choices = get_quiz()

	for _ in range(max_iterations):
		if question is None or choices is None or len(choices) != 4 or not all(isinstance(choice, str) for choice in choices) or question == "" or any(choice == "" for choice in choices):
			question, choices = get_quiz()
		else:
			break

	question_error = "Sorry, the question could not be generated. Please try again."
	choices_error = ["Try again"]
	return question or question_error, choices or choices_error

@router.get("", response_class=HTMLResponse)
async def quizzes(request: Request, user_id: int = Depends(get_authenticated_user)):
	"""
	Display the quizzes page

	Args:
		request (Request): The request object
		user_id (int, optional): The user ID. Defaults to Depends(get_authenticated_user).

	Returns:
		HTMLResponse: The response object
	"""

	return templates.TemplateResponse("quizzes.html", {"request": request})

@router.post("", response_class=HTMLResponse)
async def quizzes(request: Request, user_id: int = Depends(get_authenticated_user)):
	"""
	Display the quizzes page

	Args:
		request (Request): The request object
		user_id (int, optional): The user ID. Defaults to Depends(get_authenticated_user).

	Returns:
		HTMLResponse: The response object
	"""
	question, choices = auto_generate_quiz_until_stable()
	request.session["question"] = question
	request.session["choices"] = choices
	return templates.TemplateResponse("quiz_form.html", {"request": request, "question": question, "choices": choices})


@router.post("/answer", response_class=HTMLResponse)
async def quizzes(request: Request, user_id: int = Depends(get_authenticated_user),answer: str = Form(...)):
	"""
	Display the quizzes page

	Args:
		request (Request): The request object
		user_id (int, optional): The user ID. Defaults to Depends(get_authenticated_user).

	Returns:
		HTMLResponse: The response object
	"""
	question = request.session.get("question")
	choices = request.session.get("choices")

	correct_index = get_correct_answer(question, choices)
	feedback, color = ("Correct", "green") if (answer == choices[int(correct_index) - 1]) else ("Incorrect, the right answer is " + choices[int(correct_index) - 1], "red")
	return templates.TemplateResponse("quiz_form.html", {"request": request, "question": question, "choices": choices, "feedback": feedback, "color": color})

@router.post("/translate", response_class=HTMLResponse)
async def quizzes(request: Request, user_id: int = Depends(get_authenticated_user)):
	"""
	Display the quizzes page

	Args:
		request (Request): The request object
		user_id (int, optional): The user ID. Defaults to Depends(get_authenticated_user).

	Returns:
		HTMLResponse: The response object
	"""
	choices = list(request.session.get("choices"))
	question = request.session.get("question")
	question_translation = auto_translate_until_stable(question)

	choices_translation = []
	for i in range(len(choices)):
		choices_translation.append(auto_translate_until_stable(choices[i]))

	translation = {
		"question": question_translation,
		"choices": choices_translation
	}

	return templates.TemplateResponse("quiz_translation.html", {"request": request, "translation": translation})
