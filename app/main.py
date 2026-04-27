import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.ai_service import get_ai_response
from app.services.calendar_service import create_calendar_event, check_availability, suggest_slots, list_meetings, cancel_meeting
from app.utils.validation import validate_meeting_request

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
    max_turns = 8
    for _ in range(max_turns):
        ai_data = get_ai_response(history)
        logger.info(f"AI Response Attempt: {ai_data}")

        # ==== BACKEND VALIDATION LAYER ====
        extracted_dt = ai_data.get("datetime")
        if not extracted_dt:
            extracted_dt = ai_data.get("parameters", {}).get("datetime")
        
        val_res = {"valid": True, "action": ai_data.get("action"), "is_past": False, "is_weekend": False, "is_office_hours": True}
        if extracted_dt and extracted_dt != "null" and extracted_dt != "stored_session_datetime":
            val_res = validate_meeting_request(extracted_dt)

        debug_log = {
            "user_input": req.message,
            "parsed_datetime": extracted_dt,
            "is_past": val_res.get("is_past", False),
            "is_weekend": val_res.get("is_weekend", False),
            "is_office_hours": val_res.get("is_office_hours", True),
            "availability": "UNKNOWN",
            "final_action": "UNKNOWN"
        }

        # Override AI logic if validation fails
        should_block = not val_res["valid"]
        if should_block:
            ai_tool = ai_data.get("tool")
            is_date_query = ai_tool in ["LIST_MEETINGS", "SUGGEST_SLOTS"]
            
            if is_date_query and val_res.get("reason", "").startswith("This time is outside office hours"):
                should_block = False  # They are purely listing or checking a day. Time is irrelevant.
            if ai_tool == "LIST_MEETINGS" and val_res.get("is_past"):
                should_block = False  # They can read their history.

        if should_block:
            if ai_data.get("action") not in ["REJECT", "ASK"]:
                ai_data["action"] = val_res["action"]
                ai_data["message"] = val_res["reason"]
                ai_data["tool"] = None

            debug_log["final_action"] = ai_data["action"]
            logger.info(f"BACKEND VALIDATION LOG:\n{json.dumps(debug_log, indent=2)}")
            history.append({"role": "assistant", "content": json.dumps(ai_data)})
            return ChatResponse(
                message=ai_data.get("message") or "I could not understand that.",
                session_id=session_id,
                intent=ai_data.get("intent") or "UNKNOWN",
                action=ai_data.get("action") or "ASK",
            )
        
        # Override AI if it incorrectly says outside office hours when validation says it's valid
        if (val_res["valid"] and val_res["is_office_hours"] and 
            ai_data.get("action") == "ASK" and 
            "outside office hours" in ai_data.get("message", "").lower()):
            
            ai_data["action"] = "CONFIRM"
            ai_data["message"] = f"This time is within office hours. Would you like to proceed with scheduling the meeting at {datetime.fromisoformat(extracted_dt).strftime('%I:%M %p')}?"
            debug_log["final_action"] = "OVERRIDE_OFFICE_HOURS"
            logger.info(f"BACKEND VALIDATION LOG:\n{json.dumps(debug_log, indent=2)}")
            history.append({"role": "assistant", "content": json.dumps(ai_data)})
            return ChatResponse(
                message=ai_data.get("message"),
                session_id=session_id,
                intent=ai_data.get("intent") or "UNKNOWN",
                action=ai_data.get("action") or "CONFIRM",
            )
        # ==================================

        if ai_data.get("action") == "CALL_TOOL":
            tool_name = ai_data.get("tool")
            params = ai_data.get("parameters", {})
            
            tool_result = "Unknown tool"
            if tool_name == "CHECK_AVAILABILITY":
                dt = params.get("datetime")
                dur = params.get("duration", 30)
                available = check_availability(dt, dur)
                tool_result = "FREE" if available else "BUSY"
                debug_log["availability"] = tool_result
            
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
                dt_str = params.get("date") or params.get("datetime", "2026-04-24T00:00:00")
                date_str = dt_str.split("T")[0] if dt_str and dt_str != "null" else "2026-04-24"
                slots = suggest_slots(date_str)
                tool_result = f"AVAILABLE_SLOTS: {', '.join(slots)}"
                
            elif tool_name == "LIST_MEETINGS":
                dt_str = params.get("date") or params.get("datetime", "2026-04-24T00:00:00")
                date_str = dt_str.split("T")[0] if dt_str and dt_str != "null" else "2026-04-24"
                meetings = list_meetings(date_str)
                tool_result = f"MEETINGS:\n{meetings}"
            
            elif tool_name == "CANCEL_MEETING":
                event_id = params.get("event_id")
                if event_id:
                    tool_result = cancel_meeting(event_id)
                else:
                    tool_result = "ERROR: Missing event_id parameter"

            # Feed tool result back to AI
            debug_log["final_action"] = f"CALL_TOOL -> {tool_result}"
            logger.info(f"BACKEND VALIDATION LOG:\n{json.dumps(debug_log, indent=2)}")
            history.append({"role": "assistant", "content": json.dumps(ai_data)}) # AI's intent to call tool
            history.append({"role": "system", "content": f"TOOL_OUTPUT: {tool_result}"})
            continue # Let AI process the tool output
        
        else:
            # Check if AI is talking about availability without calling tool (only for user-like responses)
            message = ai_data.get("message", "").lower()
            extracted_dt = ai_data.get("datetime")
            
            # If AI doesn't include datetime, try to get it from previous messages
            if not extracted_dt or extracted_dt == "null":
                for msg in reversed(history):
                    if msg.get("role") == "assistant":
                        try:
                            content = json.loads(msg.get("content", "{}"))
                            if content.get("datetime") and content.get("datetime") != "null":
                                extracted_dt = content.get("datetime")
                                break
                        except:
                            continue
            
            # Debug logging
            logger.info(f"FALLBACK CHECK: message='{message}', datetime='{extracted_dt}', action='{ai_data.get('action')}'")
            
            # Only trigger fallback if AI is making availability claims without calling tool,
            # but NOT if the message is asking about duration or is a question
            if (extracted_dt and extracted_dt != "null" and 
                ai_data.get("action") != "CALL_TOOL" and
                ("available" in message or "busy" in message or "booked" in message or "unavailable" in message or "not available" in message) and
                not any(q in message for q in ["how long", "what duration", "how much time", "?"])):  # Don't trigger on questions
                
                logger.info(f"FALLBACK TRIGGERED: Forcing CHECK_AVAILABILITY for {extracted_dt}")
                # Force tool call for availability check
                ai_data["action"] = "CALL_TOOL"
                ai_data["tool"] = "CHECK_AVAILABILITY"
                ai_data["parameters"] = {"datetime": extracted_dt}
                history.append({"role": "assistant", "content": json.dumps(ai_data)})
                continue
            
            # Not a tool call, this is the final response for this turn
            debug_log["final_action"] = ai_data.get("action")
            logger.info(f"BACKEND VALIDATION LOG:\n{json.dumps(debug_log, indent=2)}")
            history.append({"role": "assistant", "content": json.dumps(ai_data)})
            return ChatResponse(
                message=ai_data.get("message") or "",
                session_id=session_id,
                intent=ai_data.get("intent") or "UNKNOWN",
                action=ai_data.get("action") or "ASK_QUESTION",
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