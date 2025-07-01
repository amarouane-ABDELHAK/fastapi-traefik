# app/main.py
from fastapi import FastAPI, Depends
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


# Create the main FastAPI app with lifespan
app = FastAPI(
    title="Main API",
    description="Main application",
    version="1.0.0",
    lifespan=lifespan
)

# Create a sub-application for the API
api_app = FastAPI(
    title="API Example",
    description="An example API with versioned routes", 
    version="1.0.0",
)

@api_app.get("/hello")
async def root():
    return {"message": "Hello Animal Enthusiast"}

@api_app.get("/health")
async def health():
    return {"status": "healthy"}

@api_app.get("/info")
async def info():
    hostname = os.uname().nodename
    return {
        "hostname": hostname,
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@api_app.get("/add")
async def add_animal(
    name: str = Query(..., description="Name of the animal"),
    db = Depends(get_db)
):
    await db.execute("INSERT INTO animals (name) VALUES ($1)", name)
    return {"message": f"Added animal: {name}"}

@api_app.get("/animals")
async def get_all_animals(db = Depends(get_db)):
    rows = await db.fetch("SELECT name FROM animals")
    return {"animals": [row["name"] for row in rows]}

# Mount the sub-application
app.mount("/api/v1", api_app)
