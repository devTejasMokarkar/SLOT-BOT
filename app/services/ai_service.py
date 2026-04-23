import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

import openai

# 1. Initialize the Client
# Use OpenAI as fallback due to Gemini quota limits
client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are an intelligent appointment scheduling assistant.
Today's date is Thursday, April 23, 2026.

Your job:
1. Understand user request for booking/rescheduling/canceling meetings
2. Extract structured data
3. ALWAYS return valid JSON only.

SUPPORTED INTENTS:
- CREATE_EVENT, CHECK_AVAILABILITY, RESCHEDULE_EVENT, CANCEL_EVENT, UNKNOWN

OUTPUT FORMAT:
{
  "intent": "CREATE_EVENT",
  "datetime": "YYYY-MM-DDTHH:MM:SS",
  "duration_minutes": 30,
  "confidence": 1.0
}

RULES:
- If time is not clear, set datetime to null.
- Return ONLY raw JSON. No markdown backticks.
"""

def extract_intent(user_message: str):
    try:
        # Prepending prompt to message to avoid 'systemInstruction' field errors in some API versions
        full_query = f"{SYSTEM_PROMPT}\n\nUser Request: {user_message}\n\nJSON Output:"

        # Use OpenAI API instead of Gemini
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"User Request: {user_message}\n\nJSON Output:"}
            ],
            temperature=0.3
        )

        if not response or not response.choices:
            raise ValueError("Empty response from AI")

        # Get the response content
        content = response.choices[0].message.content.strip()
        
        # Clean markdown if present
        clean_text = re.sub(r'^```json\s*|```$', '', content, flags=re.MULTILINE)

        return json.loads(clean_text)

    except Exception as e:
        print(f"--- DEBUG INFO ---")
        print(f"Gemini Error: {e}")
        
        # If it's a 404, let's see what models ARE available for your key
        if "404" in str(e):
            print("Attempting to list available models for your API key...")
            try:
                available_models = [m.name for m in client.models.list()]
                print(f"Available models: {available_models}")
            except:
                print("Could not retrieve model list.")
        
        return {
            "intent": "UNKNOWN",
            "datetime": None,
            "duration_minutes": 0,
            "confidence": 0.0,
            "error": "Model deprecated or unavailable. Check server logs."
        }

if __name__ == "__main__":
    # Test locally
    print(extract_intent("Book meeting tomorrow at 3pm"))