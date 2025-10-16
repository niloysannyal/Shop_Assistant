import re
from typing import Optional, List
from app.services.product_service import (
    fetch_products,
    search_by_name,
    search_by_category,
    filter_products,
    compute_actual_price
)
from app.utils.groq_client import query_groq

# Intent keyword sets (simple, easy to extend)
GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings"}
FAREWELL = {"bye", "goodbye", "see you", "take care"}
INQUIRY_PRICE = {"price", "cost", "how much", "what is the price", "priced"}
INQUIRY_STOCK = {"stock", "available", "availability", "in stock"}
INQUIRY_RATING = {"rating", "ratings", "review", "reviews", "stars"}
INQUIRY_CATEGORY = {"category", "categories", "show me", "any", "do you have"}


def _is_greeting(message: str) -> bool:
    m = message.lower()
    return any(g in m for g in GREETINGS)

def _is_farewell(message: str) -> bool:
    m = message.lower()
    return any(g in m for g in FAREWELL)

def _contains_keyword(message: str, keywords: set) -> bool:
    m = message.lower()
    return any(k in m for k in keywords)

def _normalize_word(word: str) -> str:
    word = word.lower().strip()
    # handle common plural endings
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("oes") and len(word) > 4:
        return word[:-2]
    if word.endswith("ches") or word.endswith("shes") or word.endswith("xes"):
        return word[:-2]
    if word.endswith("ses") and len(word) > 4:
        return word[:-2]
    if word.endswith("s") and len(word) > 3:
        return word[:-1]
    return word


def _extract_price_range(message: str):
    low = None; high = None
    m = re.search(r'between\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)', message, re.I)
    if m:
        return float(m.group(1)), float(m.group(2))
    m = re.search(r'(?:under|below|less than)\s+\$?(\d+(?:\.\d+)?)', message, re.I)
    if m:
        return None, float(m.group(1))
    m = re.search(r'(?:over|above|more than)\s+\$?(\d+(?:\.\d+)?)', message, re.I)
    if m:
        return float(m.group(1)), None
    return None, None

async def generate_chat_response(message: str) -> str:
    """
    Main entrypoint used by the API. Returns a user-facing string.
    """
    txt = (message or "").strip()
    if not txt:
        return "Sorry, I didn't receive a message. Please ask about a product or say 'hi'."

    # 1) greetings / farewell
    if _is_greeting(txt):
        return "Hello! 👋 How can I help you today? Ask about a product name, category, price range, or rating."
    if _is_farewell(txt):
        return "Goodbye! If you need anything else, just ask."

    # 2) load products
    products = await fetch_products()
    if not products:
        return "Sorry — I couldn't load products right now. Please try again later."

    # 3) Product identification — smarter version with plural handling
    lower_txt = txt.lower()
    norm_txt = " ".join(_normalize_word(w) for w in re.findall(r"[A-Za-z0-9\-']{2,}", lower_txt))

    # Exact title match (case-insensitive)
    exact_matches = [p for p in products if p.title.lower() == lower_txt]

    # Substring match (handles singular/plural normalization)
    if not exact_matches:
        exact_matches = [p for p in products if _normalize_word(p.title.lower()) in norm_txt]

    # Token-based fallback (with normalized tokens)
    if not exact_matches:
        tokens = [_normalize_word(t) for t in re.findall(r"[A-Za-z0-9\-']{3,}", norm_txt)]
        candidates = []
        for p in products:
            title_words = [_normalize_word(w) for w in p.title.lower().split()]
            score = len(set(tokens) & set(title_words))
            if score > 0:
                candidates.append((score, p))
        candidates.sort(reverse=True, key=lambda x: x[0])
        if candidates:
            exact_matches = [candidates[0][1]]

    name_matches = exact_matches

    # 6) If we found a product, answer
    if name_matches and not re.search(r'ratings?\s*(?:above|over|greater than)\s*\d', txt, re.I):
        product = name_matches[0]
        wants_price = _contains_keyword(txt, INQUIRY_PRICE)
        wants_stock = _contains_keyword(txt, INQUIRY_STOCK)
        wants_rating = _contains_keyword(txt, INQUIRY_RATING)

        facts = {
            "name": product.title,
            "description": product.description,
            "price": product.price,
            "discount": product.discountPercentage or 0.0,
            "actual_price": compute_actual_price(product.price, product.discountPercentage or 0.0),
            "rating": product.rating or 0.0,
            "stock": product.stock or 0,
            "brand": product.brand or "Unknown",
            "category": product.category or "Unknown"
        }

        # Short templated answers for specific intents (fast)
        if wants_price and not any([wants_stock, wants_rating]):
            return f"{facts['name']} is priced at ${facts['price']:.2f}. After a {facts['discount']:.2f}% discount the final price is ${facts['actual_price']:.2f}."
        if wants_stock and not any([wants_price, wants_rating]):
            return f"Currently we have {facts['stock']} unit(s) of {facts['name']} in stock."
        if wants_rating and not any([wants_price, wants_stock]):
            return f"{facts['name']} has an average rating of {facts['rating']} stars."

        # Build a RAG prompt for Groq to craft a human-like reply
        prompt = f"""
        You are a helpful and friendly e-commerce assistant. Use only the facts below to answer the customer's query naturally and helpfully.
        Customer message: "{message}"
        
        Product facts:
        - Name: {facts['name']}
        - Brand: {facts['brand']}
        - Category: {facts['category']}
        - Description: {facts['description']}
        - Price: ${facts['price']:.2f}
        - Discount: {facts['discount']:.2f}%
        - Final price (after discount): ${facts['actual_price']:.2f}
        - Rating: {facts['rating']}
        - Stock: {facts['stock']}
        
        Write a concise, friendly response (1–3 short paragraphs) that answers the user's question using these facts. If the user is vague, offer helpful next steps or a follow-up question.
        """
        ai_resp = query_groq(prompt)
        # If Groq fallback text, provide a local summary instead
        if ai_resp.startswith("Sorry — I couldn't reach the AI service"):
            return (f"{facts['name']} — {facts['description']} Price: ${facts['price']:.2f} "
                    f"(after {facts['discount']:.2f}% off: ${facts['actual_price']:.2f}), "
                    f"rating {facts['rating']}, stock {facts['stock']}.")
        return ai_resp

    # 7) Handle category and filter-style queries (no single product mentioned)

    # detect if user is asking about categories
    if re.search(r'\b(categories|types of products|what.*categories)\b', lower_txt):
        categories = sorted(set((p.category or "unknown").capitalize() for p in products))
        return "We currently offer products in these categories:\n- " + "\n- ".join(categories)

    # detect category mention (e.g., "show me groceries")
    categories = sorted(set((p.category or "unknown").lower() for p in products))
    for c in categories:
        if c in lower_txt:
            items = search_by_category(products, c)
            if not items:
                return f"Sorry — I couldn't find items in '{c}'."
            lines = []
            for it in items[:6]:
                actual = compute_actual_price(it.price, it.discountPercentage or 0.0)
                lines.append(
                    f"{it.title} — ${actual:.2f} (orig ${it.price:.2f}, {it.discountPercentage}% off), "
                    f"rating {it.rating}, stock {it.stock}"
                )
            return f"I found these items in *{c}*:\n" + "\n".join(lines)

    # detect price or rating filters (e.g., "under 50", "rating above 4")
    low, high = _extract_price_range(txt)
    min_rating = None
    m = re.search(r'ratings?\s*(?:above|over|greater than)\s*(\d+(?:\.\d+)?)', txt, re.I)
    if m:
        min_rating = float(m.group(1))

    filtered = filter_products(products, min_price=low, max_price=high, min_rating=min_rating)
    if filtered:
        sample = filtered[:6]
        lines = []
        for it in sample:
            actual = compute_actual_price(it.price, it.discountPercentage or 0.0)
            lines.append(
                f"{it.title} — ${actual:.2f} (orig ${it.price:.2f}, {it.discountPercentage}% off), "
                f"rating {it.rating}, stock {it.stock}"
            )
        # clarify what the filter matched
        if min_rating:
            header = f"Here are some products rated above {min_rating}:\n"
        elif high:
            header = f"Here are some products under ${high}:\n"
        elif low:
            header = f"Here are some products above ${low}:\n"
        else:
            header = "Here are some matching products:\n"
        return header + "\n".join(lines)


    # 8) Unknown / fallback -> ask Groq for a short conversational reply
    generic_prompt = f"""
    You are a friendly shopping assistant.
    The user said: "{message}"
    If the message is not specifically about a product, reply in a short conversational way,
    but avoid making up product facts. If unsure, offer guidance on what they can ask.
    """
    return query_groq(generic_prompt)
