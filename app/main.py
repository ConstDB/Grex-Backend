from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .workspaces.crud import workspace_trigger
from .db_instance import db
from .api.api_router import router
from .config.settings import settings as st
from .utils.error_handlers import register_exception_handlers
from .notifications.scheduler import start_scheduler
from ai_assistant.vectorstore.qdrant_config import setup_collection

app = FastAPI()

# Register global handlers
register_exception_handlers(app)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await db.initialize_connection()
    await setup_collection()
    await workspace_trigger()
    await start_scheduler(db.pool)
    yield
    await db.close_connection()

app = FastAPI(lifespan=lifespan)

origins = [
  "http://localhost:5173",
  "http://192.168.195.26:5173"
]
 
app.add_middleware(
  CORSMiddleware,
  # allow_origins = ["*"],
  allow_origins = origins,
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
