# 🛍️ Shop_Assistant Chatbot API

A fully functional **AI-powered product chatbot REST API** built with **FastAPI**, integrated with **Groq’s Llama 3 LLM**, and connected to **DummyJSON Products API**.  
It provides human-like conversational responses about products — prices, categories, stock, and more.

---

## 🚀 Project Overview

### 🎯 Goal
Build an intelligent **chatbot backend** that:
- Responds naturally to customer queries about products.
- Retrieves real product data from [DummyJSON Products API](https://dummyjson.com/products).
- Uses **Groq LLM (Llama 3.3 70B Versatile)** for context-aware responses.
- Supports conversational product queries like:
  - “What’s the price of Kiwi?”
  - “Do you have any groceries?”
  - “Show me products with ratings above 4.”
  - “Tell me more about Kiwi.”

---

## 🧩 Tech Stack

| Component        | Technology Used |
|------------------|-----------------|
| **Backend**      | FastAPI (Python 3.11+) |
| **AI Model**     | Groq LLM (Llama 3.3 70B Versatile) |
| **Data Source**  | DummyJSON API |
| **Frontend**     | React + TailwindCSS |
| **Testing**      | Pytest / Requests |
| **Environment**  | `.env` configuration with Pydantic |

---

## 📁 Project Structure
```
Shop_Assistant/
 ├── app/
 │    ├── api/
 │    │    └── routes_chatbot.py
 │    ├── core/
 │    │    └── config.py
 │    ├── services/
 │    │    ├── chatbot_service.py
 │    │    └── product_service.py
 │    ├── models/
 │    │    └── schemas.py
 │    ├── utils/
 │    │    └── groq_client.py
 │    └── main.py
 ├── frontend
 |    ├── index.html
 ├── .env
 ├── .gitignore
 ├── test.py
 ├── README.md
 └── requirements.txt
```


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/niloysannyal/Shop_Assistant.git
cd Shop_Assistant/
```
### 2️⃣ Create a Virtual Environment
```
python -m venv venv
source venv/bin/activate       # On macOS/Linux
venv\Scripts\activate          # On Windows
```
### 3️⃣ Install Dependencies
```
pip install -r requirements.txt
```
### 4️⃣ Configure Environment Variables
**create a .env file in the root folder and paste these variables in it.**    
**Replace "your_groq_api_key" with your groq api key**
```
GROQ_API_KEY="your_groq_api_key"
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL="llama-3.3-70b-versatile"
DUMMYJSON_URL=https://dummyjson.com/products
HOST="0.0.0.0"
PORT=8000
```
### 5️⃣ Run the API
```
uvicorn app.main:app --reload
```
🌐 **Visit the docs at:** http://localhost:8000/docs

## 💬 API Endpoints
### 🔹 GET /api/products
**Fetch and return all product data from DummyJSON.**

**Response Example:**
```
{
    "id": 18,
    "title": "Cat Food",
    "description": "Nutritious cat food formulated to meet the dietary needs of your feline friend.",
    "price": 8.99,
    "discountPercentage": 9.58,
    "rating": 3.13,
    "stock": 46,
    "brand": null,
    "category": "groceries",
    "thumbnail": "https://cdn.dummyjson.com/product-images/groceries/cat-food/thumbnail.webp"
}
```
### 🔹 POST /api/chat
**Accepts a user message and returns a natural-language AI-generated response.**

**Request Example:**
```
{
  "message": "Tell me more about Kiwi"
}
```
**Response Example:**
```
{
  "response": "Kiwi is a nutrient-rich fruit priced at $2.49, rated 4.9 stars by our customers. It ships overnight and comes with a 6-month warranty."
}
```

## 🧠 Chatbot Logic (RAG-Style)
**The chatbot uses a Retrieve-and-Generate approach:**
1. Intent Recognition → Understands user query using regex + NLP.
2. Product Retrieval → Searches DummyJSON for relevant products.
3. Fact Formatting → Extracts key details like name, price, stock, discount.
4. Response Generation → Uses Groq LLM for conversational phrasing.

### 🪄 Example Interactions
| User Message                     | Chatbot Response                          |
| -------------------------------- | ----------------------------------------- |
| “Hi”                             | Hello! 👋 How can I help you today?       |
| “Do you have groceries?”         | Lists products in the groceries category. |
| “Show me products under $10”     | Displays matching items below $10.        |
| “Is Kiwi in stock?”              | Reports real-time stock info.             |
| “What categories are available?” | Lists available categories.               |

## ✅ Testing
**To validate the chatbot and product endpoints, run:**
```
python test.py
```
🧪 Sample Output:
```
Chat tests passed: 11, failed: 0
ALL OK
```

## 🧱 Key Highlights
✅ **Modular FastAPI architecture**  
✅ **Real-time product data** from DummyJSON API  
✅ **Context-aware Groq LLM** responses  
✅ **Cached and efficient** product fetching  
✅ **Natural, context-driven** query understanding  
✅ **Friendly conversational tone**  
✅ **Beautifully responsive** React + Tailwind UI  
✅ **Animated gradients and smooth** chat experience  


## 🧑‍💻 Author

👤 **Niloy Sannyal**  
💌 **Email:** [niloysannyal@gmail.com](mailto:Niloysannyal@gmail.com)    
🐙 **GitHub:** [github/niloysannyal](https://github.com/niloysannyal)  
💼 **LinkedIn:** [linkedin.com/in/niloysannyal](https://linkedin.com/in/niloysannyal)


## 🪪 License
This project is licensed under the MIT License — free to use and modify.
