"""
API routes: /api/products and /api/chat
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import ChatRequest, ChatResponse, Product
from app.services.chatbot_service import generate_chat_response
from app.services.product_service import fetch_products

router = APIRouter(prefix="/api", tags=["Chatbot"])

@router.get("/products", response_model=List[Product])
async def get_products():
    """
    GET /api/products
    Returns the list of products fetched from DummyJSON.
    """
    products = await fetch_products()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")
    return products

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    POST /api/chat
    Accepts: {"message": "..."}
    Returns: {"response": "..."}
    """
    try:
        response_text = await generate_chat_response(request.message)
        return {"response": response_text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error generating response: {exc}")
