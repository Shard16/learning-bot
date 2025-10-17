from fastapi import FastAPI
from .routes import api_router

app = FastAPI(title="Learning Bot Backend")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "ok", "service": "learning-bot-backend"}
