from .crud import fetch_user_data_db, fetch_social_links_db
from .schemas import GetLinksResponse, GetUserResponse
import asyncpg

async def get_user_data_service(user_id: int, conn: asyncpg.Connection):
    user_data_to_fetch = ", ".join(GetUserResponse.model_fields.keys())
    link_data_to_fetch = ", ".join(GetLinksResponse.model_fields.keys())

    user_data = await fetch_user_data_db(user_id, user_data_to_fetch, conn)
    links_data = await fetch_social_links_db(user_id, link_data_to_fetch, conn)

    data = dict(user_data)

    if data["skills"] == None:
        data["skills"] = []
    data["social_links"] = dict(links_data)

    return data