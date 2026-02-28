from fastapi import APIRouter

mindy_router = APIRouter(tags=["mindy"])


@mindy_router.get("/mindy")
async def mindy():
    return {"message": "Hello Mindy!"}
