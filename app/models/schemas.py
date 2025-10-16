from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class Product(BaseModel):
    id: int
    title: str
    description: str
    price: float
    discountPercentage: Optional[float] = 0.0
    rating: Optional[float] = 0.0
    stock: Optional[int] = 0
    brand: Optional[str] = None
    category: Optional[str] = None
    thumbnail: Optional[str] = None

class SearchFilters(BaseModel):
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
