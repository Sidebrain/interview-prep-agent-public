from fastapi import FastAPI
from app.router.auth_router import router as auth_router

app = FastAPI()
app.include_router(auth_router)


@app.get("/")
async def index() -> dict:
    return {"Hello": "World"}
