# Shopfinity Support Chatbot

A professional customer support assistant built for the INNOVIAST Week 1 Assignment.

## Features
- Professional customer support persona
- In-scope: orders, returns, product questions
- Polite fallback for out-of-scope questions
- Clean, responsive UI with Streamlit
- Secure API key management

## Tech Stack
- Python 3.11+
- Streamlit for UI
- Llama 3.3 (llama-3.3-70b-versatile) via Groq API for responses
- python-dotenv for secure configuration

## Setup
1. Clone the repository
2. Create a `.env` file and add your Groq API key: `GROQ_API_KEY=your_api_key_here`
3. Run `streamlit run app.py`
