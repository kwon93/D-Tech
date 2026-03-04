from fastapi import APIRouter

janis_router = APIRouter(tags=["janis"])


@janis_router.get("/janis")
async def janis():
    return {"message": "Hello Janis!"}
