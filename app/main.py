from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from contextlib import asynccontextmanager
import os

from database import engine, Base
from routers import program, sessions, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    # Seed data if database is empty
    from seed import seed_database
    seed_database()
    yield


app = FastAPI(title="Gym Tracker", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(program.router, prefix="/api/program", tags=["program"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(stats.router, prefix="/api", tags=["stats"])


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "healthy"}
