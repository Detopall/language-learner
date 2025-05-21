#!/bin/bash
ollama serve &
sleep 5  # Give the server time to start
ollama pull llama3:latest
uvicorn main:app --host 0.0.0.0 --port 8000
