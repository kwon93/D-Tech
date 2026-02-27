from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello Wein!"}

@app.get("/mindy")
async def mindy():
    return {"message": "Hello Mindy!"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
