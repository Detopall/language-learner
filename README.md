# Japanese Learner Web App

The Japanese Learner Web App is a comprehensive platform for anyone looking to learn Japanese in a fun and effective way. Users can interact with AI-driven profiles in Japanese, practice handwriting for all three Japanese scripts, and explore a range of lessons and quizzes to build their reading, writing, listening, and speaking skills. The app also offers cultural insights and personalized learning paths to keep learners engaged and motivated.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Free Japanese Learning Resources](#free-japanese-learning-resources)

## Features

- Handwriting practice for Japanese scripts (Hiragana, Katakana, Kanji)
- Reading practice with AI-generated stories
- Quizzes with AI-generated questions and answers

## Technologies Used

- FastAPI: Python web framework for building APIs
- Htmx: JavaScript library for dynamic HTML updates
- Tailwind CSS: Utility-first CSS framework for styling
- SQLite: Database management system

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Add an empty `database.db` file in the `/database` directory
3. Run the application: `uvicorn main:app --host 0.0.0.0 --port 8000`
4. Open a web browser and navigate to `http://localhost:8000`

## Project Structure

- `main.py`: The main application file, using FastAPI framework
- `static/`: Directory for static files (images, CSS, JavaScript)
- `routes/`: Directory for API routes (auth, quizzes, etc.)
- `database/`: Directory for database schema and functions
- `handwriting/`: Directory containing handwriting prediction model and related files

## Free Japanese Learning Resources

The app provides a curated list of free Japanese learning resources, including language learning tools, textbooks, and online courses. These resources are designed to help learners of all levels improve their Japanese language skills.
