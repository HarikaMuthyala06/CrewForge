# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import connect_db, close_db
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.startups import router as startups_router
from app.routers.applications import router as applications_router
from app.routers.tasks import router as tasks_router
# Lifespan manages startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the app STARTS
    await connect_db()
    yield
    # This runs when the app STOPS
    await close_db()

# Create the FastAPI app
app = FastAPI(
    title="CrewForge API",
    description="Backend API for CrewForge — Startup Collaboration Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware — allows React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React runs here
    allow_credentials=True,
    allow_methods=["*"],   # Allow GET, POST, PUT, DELETE
    allow_headers=["*"],   # Allow all headers including Authorization
)

# Mount the authentication routes (register, login) under /api
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(startups_router, prefix="/api")
app.include_router(applications_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")

# Root endpoint — just to test the server is running
@app.get("/")
async def root():
    return {
        "message": "Welcome to CrewForge API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}