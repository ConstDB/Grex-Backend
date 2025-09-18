from .crud import fetch_user_data_db, fetch_social_links_db, partial_update_user_db, partial_update_links_db
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


async def partial_update_user_service(user_id: int, payload: dict, conn: asyncpg.Connection):

    filtered_user_payload = {
        key:value for key,value in payload.items() if value != None
    }

    old_data =  await get_user_data_service(user_id, conn)

    if "social_links" in filtered_user_payload:
        links_data = filtered_user_payload.pop("social_links")

        filtered_link_payload = {
            key:value for key,value in links_data.items() if value != None
        }

        await partial_update_links_db(user_id, filtered_link_payload, conn)

    if filtered_user_payload:
        await partial_update_user_db(user_id, filtered_user_payload, conn)
    
    
    new_data = await get_user_data_service(user_id, conn)
    
    if new_data == old_data:
        return {"message": "No changes happened."}
    
    return new_data