#!/usr/bin/env python3
"""
Simple API test script for Product Chatbot API.

Place this file in the 'server/' folder and run it while your FastAPI server is running:
    python test_api.py

It runs:
- GET /api/products  (basic schema checks)
- POST /api/chat     (several message variants)
Reports pass/fail per test and a summary.
"""
import re
import requests
import sys
import time
import json
from typing import List, Dict, Any

BASE = "http://localhost:8000/api"
PRODUCTS_URL = f"{BASE}/products"
CHAT_URL = f"{BASE}/chat"

TIMEOUT = 12

# ANSI color helpers (works on most terminals)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def ok(msg: str):
    print(f"{GREEN}✔ {msg}{RESET}")

def fail(msg: str):
    print(f"{RED}✖ {msg}{RESET}")

def info(msg: str):
    print(f"{YELLOW}→ {msg}{RESET}")

def pretty(obj: Any):
    print(json.dumps(obj, indent=2, ensure_ascii=False))

# -----------------------
# Tests
# -----------------------

def test_products_endpoint() -> bool:
    info("Testing GET /api/products ...")
    try:
        r = requests.get(PRODUCTS_URL, timeout=TIMEOUT)
    except Exception as e:
        fail(f"Request failed: {e}")
        return False

    if r.status_code != 200:
        fail(f"Expected 200 OK, got {r.status_code}: {r.text[:200]}")
        return False

    try:
        data = r.json()
    except Exception as e:
        fail(f"Invalid JSON response: {e}")
        return False

    # Data may be a list or an object; accept both shapes
    products = None
    if isinstance(data, list):
        products = data
    elif isinstance(data, dict) and "products" in data:
        products = data["products"]
    else:
        # If it's a dict but top-level is list-like under other key, try to find list value
        for v in data.values():
            if isinstance(v, list):
                products = v
                break

    if not isinstance(products, list):
        fail("Response JSON does not contain a product list.")
        pretty(data)
        return False

    if len(products) == 0:
        fail("Products list is empty.")
        return False

    # Check basic product fields existence on first item
    first = products[0]
    missing = [k for k in ("id", "title", "price", "rating") if k not in first]
    if missing:
        fail(f"Product objects missing fields: {missing}")
        pretty(first)
        return False

    ok(f"GET /api/products returned {len(products)} products and expected fields exist.")
    return True

# Chat tests: each case has:
# - message: what to send
# - expect: one of ('any', 'contains_name', 'contains_price', 'contains_category', 'list_matches', 'greeting', 'farewell')
# - extra: optional expected substring or product name
TEST_CASES = [
    # greetings / farewell
    {"message": "hi", "expect": "greeting"},
    {"message": "thanks, bye!", "expect": "farewell"},
    # product-specific
    {"message": "What's the price of Kiwi?", "expect": "contains_price", "extra": "Kiwi"},
    {"message": "Tell me more about Kiwi", "expect": "contains_name", "extra": "Kiwi"},
    {"message": "Is Cat Food in stock?", "expect": "contains_name", "extra": "Kiwi"},
    # category
    {"message": "Do you have any groceries?", "expect": "contains_category", "extra": "groceries"},
    {"message": "What categories are available?", "expect": "contains_category"},
    # filters
    {"message": "Show me products with ratings above 4", "expect": "list_matches"},
    {"message": "Show me products under 10", "expect": "list_matches"},
    # unknown / small talk
    {"message": "Tell me something random", "expect": "any"},
    {"message": "Do you have iPhones?", "expect": "any"},
]

def check_chat_response(case: Dict[str, Any], resp_text: str) -> bool:
    msg = case["message"]
    expect = case["expect"]
    extra = case.get("extra", "").lower() if case.get("extra") else ""

    txt = (resp_text or "").lower()

    # Expectation checks
    if expect == "any":
        # just ensure non-empty textual response
        return len(resp_text.strip()) >= 3

    if expect == "greeting":
        # look for hello-like words
        return any(w in txt for w in ["hello", "hi", "hey", "welcome"])

    if expect == "farewell":
        return any(w in txt for w in ["bye", "goodbye", "see you"])

    if expect == "contains_name":
        # extra should be product name; accept if mentioned or if the reply mentions price or stock
        if extra and extra in txt:
            return True
        # fallback: look for currency sign or 'price' or 'stock' words
        return any(w in txt for w in ["price", "$", "in stock", "stock", "rating", "rating of"])

    if expect == "contains_price":
        # check if response mentions numeric price or $ sign
        if "$" in resp_text:
            return True
        # numbers like 1.99 or 2
        return bool(re.search(r"\d+\.\d{1,2}|\$\d+|\d+\s?dollar", resp_text.lower()))

    if expect == "contains_category":
        # check category name present or phrase listing categories or items
        if extra and extra in txt:
            return True
        return any(w in txt for w in ["categories", "category", "i found these", "here are some items", "we have products in"])

    if expect == "list_matches":
        # look for lines with dashes or multiple entries or keywords like "here are"
        return any(phrase in txt for phrase in ["here are", "i found", "matches", "—", "- "]) or ("\n" in resp_text and len(resp_text.splitlines()) > 1)

    # default fallback
    return len(resp_text.strip()) > 0

def test_chat_endpoint() -> bool:
    info("Testing POST /api/chat with message variations ...")
    success = True
    passed = 0
    failed = 0

    for case in TEST_CASES:
        message = case["message"]
        info(f" -> Message: {message}")
        try:
            r = requests.post(CHAT_URL, json={"message": message}, timeout=TIMEOUT)
        except Exception as e:
            fail(f"Request failed: {e}")
            success = False
            failed += 1
            continue

        if r.status_code != 200:
            fail(f"Expected 200 OK, got {r.status_code}: {r.text[:200]}")
            success = False
            failed += 1
            continue

        try:
            body = r.json()
        except Exception as e:
            fail(f"Invalid JSON: {e} / Response text: {r.text[:200]}")
            success = False
            failed += 1
            continue

        resp_text = body.get("response") or body.get("answer") or ""
        if not isinstance(resp_text, str):
            fail("Response JSON does not contain a 'response' string.")
            success = False
            failed += 1
            continue

        ok_flag = check_chat_response(case, resp_text)
        if ok_flag:
            ok(f"PASS -> {message}\n   Reply: {resp_text[:200]}")
            passed += 1
        else:
            fail(f"FAIL -> {message}\n   Reply: {resp_text[:300]}")
            failed += 1
            success = False

        # small delay to avoid rapid-fire
        time.sleep(0.25)

    info(f"\nChat tests passed: {passed}, failed: {failed}")
    return success

# -----------------------
# Runner
# -----------------------
def main():
    total_ok = 0
    total_fail = 0

    info("Starting API tests against " + BASE)
    start = time.time()

    if test_products_endpoint():
        total_ok += 1
    else:
        total_fail += 1

    if test_chat_endpoint():
        total_ok += 1
    else:
        total_fail += 1

    elapsed = time.time() - start
    info(f"\nTest run finished in {elapsed:.2f}s")
    print(BOLD + ("ALL OK" if total_fail == 0 else f"FAILURES: {total_fail}") + RESET)

    # exit code non-zero on failure so CI / scripts can catch it
    sys.exit(0 if total_fail == 0 else 2)

if __name__ == "__main__":
    main()
