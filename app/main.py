from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
import logging
from .db_instance import db
from .api.api_router import router
import os
from app.task.routes import task_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger("uvicorn")

    await db.initialize_connection()

    yield

    await db.close_connection()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
  SessionMiddleware,
  secret_key=os.getenv("SESSION_SECRET")
)
app.include_router(router)
app.include_router(task_router)

@app.get("/")
async def dummy_server():
  return "Hello, Web World!"


