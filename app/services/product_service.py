"""
Product service: fetch products from DummyJSON with simple in-memory caching
and helpers for searching / filtering.
"""
import aiohttp
from typing import List, Optional
from app.core.config import settings
from app.models.schemas import Product

# simple in-memory cache (process-local). Good enough for a single container dev env.
_products_cache: Optional[List[Product]] = None

async def fetch_products() -> List[Product]:
    """
    Fetch all products from DummyJSON (cached).
    Returns a list of Product models.
    """
    global _products_cache
    if _products_cache is not None:
        return _products_cache

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(str(settings.DUMMYJSON_URL), timeout=15) as resp:
                resp.raise_for_status()
                data = await resp.json()
                products_list = data.get("products", data)
                _products_cache = [
                    Product(
                        id=int(p.get("id")),
                        title=p.get("title"),
                        description=p.get("description") or "",
                        price=float(p.get("price") or 0.0),
                        discountPercentage=float(p.get("discountPercentage", 0.0) or 0.0),
                        rating=float(p.get("rating", 0.0) or 0.0),
                        stock=int(p.get("stock", 0) or 0),
                        brand=p.get("brand"),
                        category=p.get("category"),
                        thumbnail=p.get("thumbnail")
                    ) for p in products_list
                ]
                return _products_cache
        except Exception as e:
            # In production log this; for now print so devs see the error.
            print(f"[product_service] Error fetching products: {e}")
            return []

def compute_actual_price(price: float, discount_pct: float) -> float:
    """Compute price after discount, rounded to 2 decimals."""
    try:
        return round(price * (1 - (discount_pct or 0.0) / 100.0), 2)
    except Exception:
        return price

def search_by_name(products: List[Product], query: str) -> List[Product]:
    """
    Find products with the query as a substring in title (case-insensitive).
    Returns list preserving original ordering.
    """
    q = query.strip().lower()
    if not q:
        return []
    return [p for p in products if q in p.title.lower()]

def search_by_category(products: List[Product], category: str) -> List[Product]:
    c = (category or "").strip().lower()
    if not c:
        return []
    return [p for p in products if (p.category or "").lower() == c]

def filter_products(products: List[Product], min_price: float = None, max_price: float = None, min_rating: float = None) -> List[Product]:
    out = products
    if min_price is not None:
        out = [p for p in out if p.price >= min_price]
    if max_price is not None:
        out = [p for p in out if p.price <= max_price]
    if min_rating is not None:
        out = [p for p in out if (p.rating or 0.0) >= min_rating]
    return out
