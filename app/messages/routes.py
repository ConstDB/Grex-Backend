from fastapi import APIRouter


router = APIRouter()


@router.get("/testing")
async def Testing():
    return "hello this is messaging route"