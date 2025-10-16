# Product Chatbot API 🤖

## Project Overview
This project is a RESTful Chatbot API built with FastAPI. It interacts with customers and provides human-like answers about product details using data from the [DummyJSON Products API](https://dummyjson.com/products) and Groq LLM API.

## Features
- Fetch all products: `GET /api/products`
- Chatbot endpoint: `POST /api/chat`
- AI-powered responses using Groq LLM
- Context-aware product information
- Modular FastAPI structure

## File Structure
```
server/
├── app/
│ ├── api/
│ │ ├── routes_chatbot.py
│ ├── core/
│ │ ├── config.py
│ ├── services/
│ │ ├── chatbot_service.py
│ │ ├── product_service.py
│ ├── main.py
│ ├── models/
│ │ ├── schemas.py
│ ├── utils/
│ │ ├── groq_client.py
├── requirements.txt
├── README.md
```


## Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/<username>/Product_Chatbot_API.git
cd Product_Chatbot_API/server
```
2. Create virtual environment
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Set Groq API key
```
export GROQ_API_KEY="your_groq_api_key"   # Linux/Mac
set GROQ_API_KEY="your_groq_api_key"      # Windows
```
5. Run the FastAPI server
```
uvicorn app.main:app --reload
```
6. Access API docs
Open http://localhost:8000/docs


## API Endpoints
- GET /api/products

Fetches all products from DummyJSON.

- POST /api/chat

Sends a customer message and receives an AI-generated response.

Request Example
```
{
  "message": "Tell me more about Kiwi"
}
```
Response Example
```
{
  "response": "Kiwi is a nutrient-rich fruit priced at $2.49, rated 4.9 stars by our customers. It ships overnight and comes with a 6-month warranty."
}
```

## License

MIT License


## Author

Name: Niloy Sannyal

Email: niloysannyal@gmail.com

GitHub: https://github.com/niloysannyal