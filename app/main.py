from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from .db.database import Database


db = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger("uvicorn")

    await db.initialize_connection()

    yield

    await db.close_connection()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def dummy_server():
  return "Hello, Web World!"