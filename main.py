from fastapi import FastAPI

from interview import router as interview_router

app = FastAPI()
app.include_router(interview_router)


@app.get("/")
async def root():
    return {"message": "Hello Wein!"}

@app.get("/mindy")
async def mindy():
    return {"message": "Hello Mindy!"}

@app.get("/janis")
async def janis():
    return {"message": "Hello Janis!"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
