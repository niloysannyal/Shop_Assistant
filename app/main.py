import logging
from fastapi import FastAPI
from app.api import routes_chatbot
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Product Chatbot API",
    description="FastAPI backend that answers product-related questions using DummyJSON products and Groq LLM.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_chatbot.router)

@app.get("/")
async def root():
    return {"message": "Product Chatbot API is running. Open /docs for interactive docs."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
