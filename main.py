import sqlite3
from routes.auth import router as auth_router
from routes.auth import get_authenticated_user
from routes.api import router as api_router
from config import get_templates

import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from database.db import create_tables

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


@app.get("/")
async def root():
    return FileResponse(f"{STATIC_FOLDER}/index.html")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, _: int = Depends(get_authenticated_user)):
    templates = get_templates()
    request.session["home"] = True
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "home": True}
    )


# Include API routes
app.include_router(auth_router, prefix="/auth")
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
