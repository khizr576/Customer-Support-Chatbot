# pyrefly: ignore [missing-import]
import streamlit as st
import openai
import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv(override=True)


# Initialize OpenAI client pointing to Groq
api_key = os.getenv("GROQ_API_KEY")
if api_key and not api_key.startswith("your-groq-api-key"):
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )
else:
    client = None


# ============================================
# PROFESSIONAL SYSTEM PROMPT - CUSTOMER SUPPORT
# ============================================
SYSTEM_PROMPT = """You are Aria, a professional customer support assistant for Shopfinity, a premium online retail brand.

## Your Role & Goal
Provide helpful, empathetic, and efficient support for post-purchase inquiries. Your goal is to resolve 70-80% of customer questions independently.

## What You Can Help With:
- Order tracking and delivery status
- Returns and exchanges (check eligibility first)
- Refund inquiries (explain timelines clearly)
- Product questions (use catalog information)
- Account and payment issues
- Shipping and delivery delays

## What You CANNOT Help With:
- Technical website bugs (escalate these)
- Complex billing disputes beyond standard refunds
- Questions about competitor products
- Anything outside Shopfinity's products/services

## Your Tone:
- Warm, clear, and confident - like a trained store assistant
- Professional but empathetic (calm concierge, not peppy call center)
- Keep responses concise (2-3 sentences unless the customer asks for details)

## RULES (CRITICAL):
1. NEVER guess. If you don't know something, say so and offer alternatives
2. If you can't resolve an issue in 2 attempts, offer to escalate: "Let me connect you with a specialist who can better assist you."
3. ALWAYS confirm actions before doing them: "Just to confirm, you'd like to return your recent order - is that right?"
4. DON'T use negative language like "impossible," "can't help," or "not my job"

## Example Responses:
✅ Good: "I can help you track your order. Could you please provide your order number?"
✅ Good: "I understand the delay is frustrating. Let me check the status for you right away."
✅ Good: "I don't have that information, but I can connect you to someone who does."

❌ Bad: "Sorry, I can't help with that." (too blunt, unhelpful)
❌ Bad: "I think maybe your order is..." (guessing is not allowed)
❌ Bad: "That's impossible to do." (unprofessional, negative)

## Business Information:
- Hours: Monday-Friday, 9am-6pm ET
- Return policy: 30-day returns, free shipping on returns
- Contact escalation: support@shopfinity.com

Remember: Be helpful, honest, and professional. If in doubt, escalate with context."""

# ============================================
# FALLBACK RESPONSES (when API fails or out of scope)
# ============================================
FALLBACK_RESPONSES = [
    "I'm sorry, I can only help with questions about orders, returns, and products at Shopfinity. Is there something specific about your order I can assist with?",
    "I don't have information about that topic. I'm here to help with Shopfinity purchases - orders, tracking, returns, and product questions.",
    "That's outside my scope. For questions about our products or your orders, I'd be happy to help. What can I assist you with?",
]

ESCALATION_MESSAGE = "I'm not able to resolve this fully. Let me connect you with a specialist who can better assist you. Please email support@shopfinity.com with your order details, and they'll get back to you within 24 hours."

# ============================================
# CORE CHAT FUNCTION
# ============================================
def get_bot_response(user_message):
    """Generate response with proper error handling and fallback behavior"""
    
    # Empty input check
    if not user_message or user_message.strip() == "":
        return "Please type a question so I can help you."
        
    if client is None:
        return "I'm sorry, I cannot respond because the Groq API key is not configured. Please set your API key in a `.env` file."
    
    # Out-of-scope detection (simple keyword check - bot prompt handles the rest)
    try:
        # Build conversation history for context
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]
        # Add last 5 messages for context
        for msg in st.session_state.messages[-5:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        reply = response.choices[0].message.content
        
        # Check if we need to escalate (if bot mentioned escalation keywords)
        if "specialist" in reply.lower() or "connect you with" in reply.lower():
            st.session_state.fallback_count += 1
        else:
            st.session_state.fallback_count = 0
        
        # If fallback count reaches 2, force escalation
        if st.session_state.fallback_count >= 2:
            reply = ESCALATION_MESSAGE
            
        return reply
        
    except openai.OpenAIError as e:
        # API error handling
        st.session_state.fallback_count += 1
        if st.session_state.fallback_count >= 2:
            return ESCALATION_MESSAGE
        return "I'm having trouble connecting right now. Please try again or email support@shopfinity.com for immediate help."
        
    except Exception as e:
        # General error handling
        return "I encountered an unexpected issue. Please refresh the page or contact support@shopfinity.com if the problem persists."

# ============================================
# STREAMLIT UI (WRAPPED FOR DIRECT EXECUTION SUPPORT)
# ============================================
def main():
    st.set_page_config(
        page_title="Shopfinity Support",
        page_icon="🛍️",
        layout="centered"
    )

    # Custom CSS for professional look
    st.markdown("""
        <style>
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .stChatMessage.user {
            background-color: #e3f2fd;
        }
        .stChatMessage.assistant {
            background-color: #f5f5f5;
        }
        .stApp {
            max-width: 800px;
            margin: 0 auto;
        }
        .stTextInput > div > div > input {
            border-radius: 25px;
            padding: 12px 20px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🛍️ Shopfinity Support")
    st.caption("I'm Aria, your professional customer support assistant. I can help with orders, returns, and product questions.")

    if client is None:
        st.warning("⚠️ **Groq API Key is missing or invalid.** Please configure your `GROQ_API_KEY` in a `.env` file in the root directory to enable the chatbot.")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm Aria from Shopfinity support. How can I help you today with your order or product questions?"}
        ]
    if "fallback_count" not in st.session_state:
        st.session_state.fallback_count = 0

    # ============================================
    # DISPLAY CHAT HISTORY
    # ============================================
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ============================================
    # USER INPUT HANDLING
    # ============================================
    if prompt := st.chat_input("Ask about your order, returns, or products...", disabled=(client is None)):
        # Add user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get and display bot response
        with st.chat_message("assistant"):
            response = get_bot_response(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Add small delay for realistic feel
        time.sleep(0.1)

    # ============================================
    # FOOTER WITH ESCALATION INFO
    # ============================================
    st.divider()
    st.caption("💡 If I can't help, you can always email **support@shopfinity.com** for assistance.")

if __name__ == "__main__":
    if st.runtime.exists():
        main()
    else:
        import sys
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", __file__]
        sys.exit(stcli.main())


