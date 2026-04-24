import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
import google.generativeai as genai
import anthropic
import openai

load_dotenv()

# Initialize API Clients
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
openrouter_client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

SYSTEM_PROMPT = """
You are an intelligent scheduling assistant.
Today's date is Friday, April 24, 2026.

Your job is to:
1. Understand user intent (schedule, check, cancel meeting)
2. Extract date, time, and duration
3. Follow strict business rules before scheduling
4. Ask clarifying questions when needed
5. NEVER assume missing data
6. NEVER schedule directly — always call tools

---

### AVAILABLE TOOLS:

1. CHECK_AVAILABILITY(datetime, duration)
   → returns: FREE / BUSY

2. CREATE_MEETING(datetime, duration)
   → schedules meeting

3. SUGGEST_SLOTS(datetime_range)
   → returns available slots

---

### BUSINESS RULES:

- Office hours: 9:00 AM – 6:00 PM
- If meeting is outside office hours:
  → Ask: "This is outside office hours. Do you want to continue?"

- If slot is BUSY:
  → Do NOT schedule
  → Suggest alternative slots

- Always confirm before booking:
  → "Do you want to confirm this meeting?"
  → AFTER user confirms: YOU MUST FIRST CALL THE TOOL 'CREATE_MEETING'.
  → ONLY AFTER tool returns success, you return action 'SUCCESS'.

---

### CONVERSATION RULES:

- Be concise, human-like, and professional
- Ask one question at a time
- Maintain conversation state
- Handle ambiguous input (e.g., "tomorrow evening")

---

### OUTPUT FORMAT:

Respond in JSON only:
{
  "intent": "SCHEDULE | CHECK | CANCEL | UNKNOWN",
  "message": "Response message to the user",
  "action": "ASK_QUESTION | ASK_CONFIRMATION | CALL_TOOL | SUCCESS | ERROR",
  "tool": "CHECK_AVAILABILITY | CREATE_MEETING | SUGGEST_SLOTS | null",
  "parameters": {
    "datetime": "YYYY-MM-DDTHH:MM:SS",
    "duration": 30
  }
}
"""

SUMMARIZATION_PROMPT = """
Summarize the following scheduling conversation history into key points.
Return only the summarized context of what has been agreed or discussed so far.
Focus on: Intent, Date/Time, Duration, and Confirmations.
"""

def summarize_history(messages: List[Dict]) -> str:
    """Summarizes history if it gets too long to save tokens."""
    try:
        # Use Gemini for summarization as it's usually cheaper/faster for this
        model = genai.GenerativeModel("gemini-1.5-flash")
        text_to_summarize = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        response = model.generate_content(f"{SUMMARIZATION_PROMPT}\n\nHistory:\n{text_to_summarize}")
        return response.text if response.text else "Previously discussed scheduling."
    except:
        return "Context: Scheduling in progress."

def get_ai_response(messages: List[Dict]):
    """
    Sends history to AI with fallback logic: Gemini -> Claude -> Error.
    Summarizes history if > 6 messages (3+ turns).
    """
    # 1. Summarization check
    if len(messages) > 6:
        summary = summarize_history(messages[:-2]) # Summarize everything except the last turn
        messages = [
            {"role": "system", "content": f"SUMMARY OF PREVIOUS CONVERSATION: {summary}"},
            messages[-2], # Last user message
            messages[-1]  # Most recent context
        ]

    # 2. Try Gemini
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro", # Using Pro as Flash often has lower quota
            system_instruction=SYSTEM_PROMPT,
            generation_config={"response_mime_type": "application/json"}
        )
        gemini_history = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        last_msg = gemini_history.pop()
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(last_msg["parts"][0])
        return json.loads(response.text.strip())
        
    except Exception as e:
        print(f"Gemini failed or quota reached: {e}")
        
        # 3. Fallback to Claude (Anthropic)
        try:
            print("Falling back to Claude...")
            # Prepare messages for Claude (it doesn't like system messages in history usually)
            claude_messages = []
            for msg in messages:
                if msg["role"] == "system": continue
                claude_messages.append({"role": msg["role"] if msg["role"] == "user" else "assistant", "content": msg["content"]})
            
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=claude_messages
            )
            content = response.content[0].text.strip()
            # Clean possible markdown
            content = re.sub(r'^```json\s*|```$', '', content, flags=re.MULTILINE)
            return json.loads(content)
            
        except Exception as e:
            print(f"Claude failed or quota reached: {e}")
            
            # 4. Fallback to OpenAI
            try:
                print("Falling back to OpenAI...")
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *messages
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content.strip())
            except Exception as e:
                print(f"OpenAI failed or quota reached: {e}")
                
                # 5. Fallback to OpenRouter (GPT-4o-Mini)
                try:
                    print("Falling back to OpenRouter...")
                    response = openrouter_client.chat.completions.create(
                        model="openai/gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            *messages
                        ],
                        response_format={"type": "json_object"}
                    )
                    return json.loads(response.choices[0].message.content.strip())
                except Exception as e:
                    print(f"OpenRouter failed: {e}")
                    return {
                        "intent": "UNKNOWN",
                        "message": "Quota reached for all AI services. Please try again later.",
                        "action": "ERROR",
                        "tool": None,
                        "parameters": {}
                    }

if __name__ == "__main__":
    test_history = [{"role": "user", "content": "Schedule meeting tomorrow at 10am"}]
    print(json.dumps(get_ai_response(test_history), indent=2))