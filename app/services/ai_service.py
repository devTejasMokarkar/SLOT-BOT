import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
import openai

load_dotenv()

# Initialize only OpenRouter client
openrouter_client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

SYSTEM_PROMPT = """
You are an AI Scheduling Assistant.

Your ONLY responsibility is:
1. Understand user intent
2. Extract structured data (date; and time/duration if specific)
3. Guide conversation step-by-step

You MUST NOT:
- Assume availability
- Schedule meetings directly
- Ignore business rules

---

### BUSINESS CONTEXT:

- Working Days: Monday to Friday
- Working Hours: 09:30 AM – 06:30 PM
- Timezone: Asia/Kolkata

STRICT RULES:
- Never allow scheduling in the past
- If user gives past time → inform and ask for new time
- If weekend → inform office is closed
- If outside working hours → ask confirmation
- Always confirm before final booking

---

### TOOL USAGE:

Available tools:

1. CHECK_AVAILABILITY(datetime, duration)
2. CREATE_MEETING(datetime, duration)
3. SUGGEST_SLOTS(date)
4. LIST_MEETINGS(date) - returns a list of events scheduled on the date along with their event_ids
5. CANCEL_MEETING(event_id) - cancels an event (use LIST_MEETINGS first to obtain the event_id if unknown)

---

### CONVERSATION FLOW:

STEP 1: Extract intent + datetime
STEP 2: Validate logically (basic checks)
STEP 3: Ask user confirmation if needed
STEP 4: Call tool ONLY after confirmation

---

### RESPONSE FORMAT (STRICT JSON):

{
  "intent": "SCHEDULE | CHECK | CANCEL",
  "datetime": "ISO format or null",
  "message": "human readable response",
  "action": "ASK | CONFIRM | CALL_TOOL | REJECT",
  "tool": "CHECK_AVAILABILITY | CREATE_MEETING | SUGGEST_SLOTS | LIST_MEETINGS | CANCEL_MEETING | null",
  "parameters": {}
}

---

### BEHAVIOR RULES:

- Be conversational but precise
- Ask one question at a time
- If input is ambiguous → ask clarification
- NEVER hallucinate availability or say "busy"/"available" without calling tools
- ALWAYS call CHECK_AVAILABILITY tool before saying anything about availability
- NEVER say: "I can't check meetings" → You MUST use tools
- IF USER CONFIRMS scheduling → MUST call CHECK_AVAILABILITY tool first

---

### INTENT RULES (STRICT):

- If user asks to "check", "list", "show", "any meetings"
  → intent = CHECK
  → DO NOT ask for time or duration
- For CHECK:
  → Only extract date
  → Call LIST_MEETINGS(date)

---

### EXAMPLES:

User: "Schedule meeting 24/04/2026 7:30 PM"

Response:
{
  "intent": "SCHEDULE",
  "datetime": "2026-04-24T19:30:00",
  "message": "This is outside office hours (09:30 AM – 06:30 PM). Do you still want to proceed?",
  "action": "ASK"
}

---

User: "Schedule meeting yesterday"

Response:
{
  "intent": "SCHEDULE",
  "datetime": null,
  "message": "You cannot schedule a meeting in the past. Please provide a valid future date and time.",
  "action": "REJECT"
}

---

User: "Schedule meeting Sunday 3 PM"

Response:
{
  "intent": "SCHEDULE",
  "datetime": "2026-04-26T15:00:00",
  "message": "Our office is closed on weekends. Please choose a weekday.",
  "action": "REJECT"
}

---

User: "Yes proceed"

Response:
{
  "intent": "SCHEDULE",
  "action": "CALL_TOOL",
  "tool": "CHECK_AVAILABILITY",
  "parameters": {
    "datetime": "stored_session_datetime"
  }
}

---

User: "check meetings monday"

Response:
{
  "intent": "CHECK",
  "action": "CALL_TOOL",
  "tool": "LIST_MEETINGS",
  "parameters": {
    "date": "2026-04-27"
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
        # Use OpenRouter for summarization
        text_to_summarize = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
        response = openrouter_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": SUMMARIZATION_PROMPT},
                {"role": "user", "content": f"History:\n{text_to_summarize}"}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip() if response.choices[0].message.content else "Previously discussed scheduling."
    except:
        return "Context: Scheduling in progress."

def get_ai_response(messages: List[Dict]):
    """
    Sends history to OpenRouter AI service only.
    Summarizes history if > 6 messages (3+ turns).
    """
    from datetime import datetime
    current_date_str = datetime.now().strftime("%A, %B %d, %Y")
    dynamic_system_prompt = f"Today's date is {current_date_str}.\n" + SYSTEM_PROMPT

    # 1. Summarization check
    if len(messages) > 6:
        summary = summarize_history(messages[:-2]) # Summarize everything except the last turn
        messages = [
            {"role": "system", "content": f"SUMMARY OF PREVIOUS CONVERSATION: {summary}"},
            messages[-2], # Last user message
            messages[-1]  # Most recent context
        ]

    # 2. Use OpenRouter only
    try:
        response = openrouter_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": dynamic_system_prompt},
                *messages
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"OpenRouter failed: {e}")
        return {
            "intent": "UNKNOWN",
            "message": "AI service unavailable. Please try again later.",
            "action": "ERROR",
            "tool": None,
            "parameters": {}
        }

if __name__ == "__main__":
    test_history = [{"role": "user", "content": "Schedule meeting tomorrow at 10am"}]
    print(json.dumps(get_ai_response(test_history), indent=2))