import os
import json
import re
from typing import List, Dict
from dotenv import load_dotenv
import openai

load_dotenv()

def extract_meeting_title(user_message: str) -> str:
    """
    Extract meeting title from natural language input following the SMART CONTEXT rules.
    
    Examples:
    "schedule meeting tomorrow 5 pm for milestone card" → "milestone card meet"
    "book meeting about project sync at 4 pm" → "project sync meet"
    "schedule meeting tomorrow 3 pm" → "Meeting" (fallback)
    """
    message_lower = user_message.lower()
    
    # Keywords that indicate title context
    title_keywords = ["for", "about", "regarding", "on"]
    
    for keyword in title_keywords:
        # Look for pattern: keyword + <title phrase>
        # More flexible pattern that handles time references better
        pattern = rf'{keyword}\s+([^,.(]+?)(?:\s+(?:with|and|tomorrow|today|at|on|in|$|,|\.)|$)'
        match = re.search(pattern, message_lower)
        if match:
            title_phrase = match.group(1).strip()
            # Clean up the phrase - remove time-related words
            title_phrase = re.sub(r'\b(at|on|in|with|and|tomorrow|today|\d{1,2}(:\d{2})?\s*(am|pm))\b', '', title_phrase).strip()
            
            # Remove extra words that don't belong to title
            title_phrase = re.sub(r'\b(meeting|schedule|book|appointment)\b', '', title_phrase).strip()
            
            if title_phrase and len(title_phrase) > 1:
                return f"{title_phrase} meet"
    
    # Fallback: Look for meaningful phrases without keywords
    # Try to find noun phrases that could be titles
    patterns = [
        r'meeting\s+(.+?)\s+(?:tomorrow|today|at|on|in|with|$)',
        r'book\s+(.+?)\s+(?:tomorrow|today|at|on|in|with|$)',
        r'schedule\s+(.+?)\s+(?:tomorrow|today|at|on|in|with|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            title_phrase = match.group(1).strip()
            # Clean up
            title_phrase = re.sub(r'\b(at|on|in|with|and|tomorrow|today|\d{1,2}(:\d{2})?\s*(am|pm))\b', '', title_phrase).strip()
            title_phrase = re.sub(r'\b(meeting|schedule|book|appointment)\b', '', title_phrase).strip()
            
            if title_phrase and len(title_phrase) > 1:
                return f"{title_phrase} meet"
    
    # Final fallback
    return "Meeting"

def extract_email_attendees(user_message: str) -> List[str]:
    """
    Extract email addresses from natural language input.
    
    Example:
    "schedule meeting tomorrow 5 pm for milestone card with john@gmail.com and test@company.com"
    → ["john@gmail.com", "test@company.com"]
    """
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, user_message)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_emails = []
    for email in emails:
        if email.lower() not in seen:
            seen.add(email.lower())
            unique_emails.append(email)
    
    return unique_emails

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
    except Exception as e:
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str or "user not found" in error_str:
            return "Context: Scheduling in progress (API auth issue)."
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
            response_format={"type": "json_object"},
            max_tokens=200,  # Limit response length
            temperature=0.3  # Lower temperature for faster, more consistent responses
        )
        return json.loads(response.choices[0].message.content.strip())
    except Exception as e:
        print(f"OpenRouter failed: {e}")
        error_str = str(e).lower()
        
        # Check for authentication errors
        if "401" in error_str or "unauthorized" in error_str or "user not found" in error_str:
            return {
                "intent": "UNKNOWN",
                "message": "🔑 Authentication tokens have expired or are invalid. Please refresh your API keys and try again later.",
                "action": "ERROR",
                "tool": None,
                "parameters": {}
            }
        elif "429" in error_str or "rate limit" in error_str:
            return {
                "intent": "UNKNOWN", 
                "message": "⏱️ Rate limit exceeded. Please try again in a few moments.",
                "action": "ERROR",
                "tool": None,
                "parameters": {}
            }
        else:
            return {
                "intent": "UNKNOWN",
                "message": "🤖 AI service temporarily unavailable. Please try again later.",
                "action": "ERROR",
                "tool": None,
                "parameters": {}
            }

if __name__ == "__main__":
    test_history = [{"role": "user", "content": "Schedule meeting tomorrow at 10am"}]
    print(json.dumps(get_ai_response(test_history), indent=2))