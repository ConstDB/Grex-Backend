from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .workspaces.crud import workspace_trigger
import logging
from .db_instance import db
from .api.api_router import router
from .config.settings import settings as st
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = logging.getLogger("uvicorn")

    await db.initialize_connection()
    await workspace_trigger()
    yield

    await db.close_connection()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_credentials=True,
  allow_methods = ["*"],
  allow_headers = ["*"]
)

app.add_middleware(
  SessionMiddleware,
  secret_key=st.SESSION_SECRET
)

app.include_router(router)

@app.get("/")
async def dummy_server():
  return "Hello, Web World!"


