import asyncio
import asyncpg
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging
from ..config.settings import settings as st

logger = logging.getLogger("uvicorn")


load_dotenv()

class Database:

    def __init__(self, database=st.POSTGRES_DB, host="localhost", user=st.POSTGRES_USER, password=st.POSTGRES_PASSWORD, port=5432):
        self.pool = None
        self.database = database
        self.host = host
        self.password = password
        self.user = user
        self.port = port 

    async def initialize_connection(self, max_retries=5, base_delay=0.5):
        
        for attempt in range(1, max_retries + 1):
            try:
                self.pool = await asyncpg.create_pool(
                    database=self.database,
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port      
                )

                logger.info("Database initialized successfully")
                break

            except Exception as e:
                logger.warning(f"Database initialization failed (attempt {attempt} -> {e})")

                if attempt < max_retries:
                    base_delay = min(6.0, base_delay * (2 ** (attempt - 1)))
                    logger.warning(f"Retrying in {base_delay} seconds.")
                    await asyncio.sleep(base_delay)
                else:
                    logger.error("Max retries reached. Could not connect to database.")
                    raise
    
    @asynccontextmanager
    async def get_connection(self):
        if self.pool is None:
            raise Exception("Database not initialized. Call Database.initialize() first.")
        try:
            conn = await self.pool.acquire()
            yield conn
        finally:
            await self.release_connection(conn)	

    async def release_connection(self, conn):
        await self.pool.release(conn)

    async def close_connection(self):
        if self.pool is not None:
            await self.pool.close()

