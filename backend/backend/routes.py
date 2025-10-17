from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health")
async def health():
    return {"healthy": True}

# Placeholder routes
@api_router.post("/upload_pdf")
async def upload_pdf():
    return {"status": "received"}

@api_router.post("/generate_summary")
async def generate_summary():
    return {"summary": "This is a placeholder."}
