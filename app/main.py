import os
import json
import logging
from typing import List, Optional, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.ai_service import get_ai_response
from app.services.calendar_service import create_calendar_event, check_availability, suggest_slots


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Appointment Agent API",
    description="Intelligent multi-turn appointment scheduling",
    version="2.0.0"
)

# In-memory session store
sessions: Dict[str, List[Dict]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_user"

class ChatResponse(BaseModel):
    message: str
    session_id: str
    intent: str
    action: str
    event_id: Optional[str] = None
    event_link: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Appointment Agent API v2.0.0"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id
    if session_id not in sessions:
        sessions[session_id] = []
    
    history = sessions[session_id]
    history.append({"role": "user", "content": req.message})

    # Agent Loop
    max_turns = 3
    for _ in range(max_turns):
        ai_data = get_ai_response(history)
        logger.info(f"AI Response Attempt: {ai_data}")

        if ai_data.get("action") == "CALL_TOOL":
            tool_name = ai_data.get("tool")
            params = ai_data.get("parameters", {})
            
            tool_result = "Unknown tool"
            if tool_name == "CHECK_AVAILABILITY":
                dt = params.get("datetime")
                dur = params.get("duration", 30)
                available = check_availability(dt, dur)
                tool_result = "FREE" if available else "BUSY"
            
            elif tool_name == "CREATE_MEETING":
                dt = params.get("datetime")
                dur = params.get("duration", 30)
                res = create_calendar_event(dt, "Meeting", dur)
                if res.get("success"):
                    tool_result = f"SUCCESS: Event ID {res.get('event_id')}"
                    ai_data["event_id"] = res.get("event_id")
                    ai_data["event_link"] = res.get("event_link")
                else:
                    tool_result = f"ERROR: {res.get('error')}"
            
            elif tool_name == "SUGGEST_SLOTS":
                # Extract date from datetime or use today
                dt_str = params.get("datetime", "2026-04-24T00:00:00")
                date_str = dt_str.split("T")[0]
                slots = suggest_slots(date_str)
                tool_result = f"AVAILABLE_SLOTS: {', '.join(slots)}"

            # Feed tool result back to AI
            history.append({"role": "assistant", "content": json.dumps(ai_data)}) # AI's intent to call tool
            history.append({"role": "system", "content": f"TOOL_OUTPUT: {tool_result}"})
            continue # Let AI process the tool output
        
        else:
            # Not a tool call, this is the final response for this turn
            history.append({"role": "assistant", "content": json.dumps(ai_data)})
            return ChatResponse(
                message=ai_data.get("message", ""),
                session_id=session_id,
                intent=ai_data.get("intent", "UNKNOWN"),
                action=ai_data.get("action", "ASK_QUESTION"),
                event_id=ai_data.get("event_id"),
                event_link=ai_data.get("event_link")
            )

    return ChatResponse(
        message="I'm thinking too much. Let's start over.",
        session_id=session_id,
        intent="UNKNOWN",
        action="ERROR"
    )

@app.get("/health")
async def health():
    return {"status": "ok"}