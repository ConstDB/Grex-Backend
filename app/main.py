from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from .db.database import Database
from .api.api_router import router

db = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger("uvicorn")

    await db.initialize_connection()

    yield

    await db.close_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/")
async def dummy_server():
  return "Hello, Web World!"