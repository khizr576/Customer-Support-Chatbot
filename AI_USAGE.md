# AI Usage Documentation

## Tools Used
- OpenAI GPT-3.5-turbo API
- Streamlit for interface

## System Prompt Strategy
The prompt defines:
- Persona: Aria, professional support assistant
- Scope: Orders, returns, products only
- Tone: Warm, clear, professional
- Rules: No guessing, escalate when needed, positive language

## Limitations
- Cannot access live order data (no database integration yet)
- Works best for basic support inquiries
- May struggle with highly complex or multi-part questions

## Improvements Made
- Added escalation after 2 fallback attempts
- Custom error messages for API issues
- Professional styling for better UX
