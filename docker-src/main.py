# app/main.py
from fastapi import FastAPI, Depends, APIRouter
import os
import asyncpg
from fastapi import Query
from contextlib import asynccontextmanager


DATABASE_URL = os.getenv("DATABASE_URL")


@asynccontextmanager
async def lifespan(app):
    app.state.db = await asyncpg.connect(DATABASE_URL)
    await app.state.db.execute("""
        CREATE TABLE IF NOT EXISTS animals (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
    """)
    yield
    await app.state.db.close()


# Dependency to get database connection
async def get_db():
    return app.state.db


app = FastAPI(
    docs_url=None,
    redoc_url=None,
)

# Create a sub-application for the API
api_app = FastAPI(
    title="K8s 102 - FastAPI",
    description="An example API for K8s", 
    version="1.0.0",
)

router = APIRouter()


@router.get("/hello")
async def root():
    return {"message": "Hello Animal Enthusiast"}

@router.get("/health")
async def health():
    return {"status": "healthy"}

@router.get("/info")
async def info():
    hostname = os.uname().nodename
    return {
        "hostname": hostname,
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@router.get("/add")
async def add_animal(
    name: str = Query(..., description="Name of the animal"),
    db = Depends(get_db)
):
    await db.execute("INSERT INTO animals (name) VALUES ($1)", name)
    return {"message": f"Added animal: {name}"}

@router.get("/animals")
async def get_all_animals(db = Depends(get_db)):
    rows = await db.fetch("SELECT name FROM animals")
    return {"animals": [row["name"] for row in rows]}

api_app.include_router(router)


# Mount the sub-application
app.mount("/api/v1", api_app)
