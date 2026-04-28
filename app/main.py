import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.ai_service import get_ai_response
from app.services.calendar_service import create_calendar_event, check_availability, suggest_slots, list_meetings, cancel_meeting, create_meeting_tool, list_available_slots
from app.services.slotbot_state_machine import process_slotbot_message
from app.services.slotbot_ui_state_machine import process_slotbot_ui_message
from app.utils.validation import validate_meeting_request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Appointment Agent API",
    description="Intelligent multi-turn appointment scheduling",
    version="2.0.0"
)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# In-memory session store
sessions: Dict[str, List[Dict]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_user"

class ChatResponse(BaseModel):
    state: str
    message: str
    action: str
    tool: Optional[str] = None
    parameters: Optional[Dict] = None
    session_id: str
    event_id: Optional[str] = None
    event_link: Optional[str] = None

class UIChatRequest(BaseModel):
    message: Optional[str] = ""
    session_id: Optional[str] = "default_user"
    selected_action: Optional[str] = None
    selected_date: Optional[str] = None
    selected_slot: Optional[str] = None

class UIChatResponse(BaseModel):
    intent: str
    date: str
    selected_slot: str
    message: str
    action: str
    tool: Optional[str] = None
    parameters: Optional[Dict] = None
    session_id: str
    event_id: Optional[str] = None
    event_link: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Appointment Agent API v2.0.0"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """SlotBot State Machine Endpoint"""
    session_id = req.session_id
    
    try:
        # Process message through state machine
        response = process_slotbot_message(req.message, session_id)
        
        logger.info(f"SlotBot Response: {response}")
        
        # Handle tool execution if needed
        event_id = None
        event_link = None
        
        if response.get("action") == "CALL_TOOL" and response.get("tool"):
            tool_name = response.get("tool")
            params = response.get("parameters", {})
            
            if tool_name == "CREATE_MEETING":
                dt = params.get("datetime")
                dur = params.get("duration", 30)
                
                # Additional validation before creating
                if not dt or dt == "null":
                    response["message"] = "❌ No datetime provided for meeting"
                    response["action"] = "ERROR"
                    return ChatResponse(
                        state=response.get("state", "ERROR"),
                        message=response["message"],
                        action=response["action"],
                        session_id=session_id
                    )
                
                res = create_calendar_event(dt, "Meeting", dur)
                if res.get("success"):
                    event_id = res.get("event_id")
                    event_link = res.get("event_link")
                    response["message"] = f"✅ Meeting scheduled successfully"
                    # Verify it was actually created by checking calendar
                    from app.services.calendar_service import list_meetings
                    date_str = dt.split("T")[0]
                    meetings_after = list_meetings(date_str)
                    if event_id and event_id not in meetings_after:
                        response["message"] = "❌ Meeting creation failed - not found in calendar"
                        response["action"] = "ERROR"
                else:
                    response["message"] = f"❌ Failed to create meeting: {res.get('error')}"
                    response["action"] = "ERROR"
            
            elif tool_name == "CHECK_AVAILABILITY":
                dt = params.get("datetime")
                dur = params.get("duration", 30)
                available = check_availability(dt, dur)
                response["message"] = "Slot is available" if available else "Slot is busy"
                response["action"] = "CONFIRM" if available else "ASK"
            
            elif tool_name == "LIST_MEETINGS":
                dt_str = params.get("date") or params.get("datetime", "2026-04-24T00:00:00")
                date_str = dt_str.split("T")[0] if dt_str and dt_str != "null" else "2026-04-24"
                meetings = list_meetings(date_str)
                response["message"] = f"Meetings:\n{meetings}"
                response["action"] = "COMPLETE"
            
            elif tool_name == "SUGGEST_SLOTS":
                dt_str = params.get("date") or params.get("datetime", "2026-04-24T00:00:00")
                date_str = dt_str.split("T")[0] if dt_str and dt_str != "null" else "2026-04-24"
                slots = suggest_slots(date_str)
                response["message"] = f"Available slots: {', '.join(slots)}"
                response["action"] = "COMPLETE"
            
            elif tool_name == "CANCEL_MEETING":
                event_id_param = params.get("event_id")
                if event_id_param:
                    result = cancel_meeting(event_id_param)
                    response["message"] = result
                    response["action"] = "COMPLETE"
                else:
                    response["message"] = "ERROR: Missing event_id parameter"
                    response["action"] = "ERROR"
        
        return ChatResponse(
            state=response.get("state", "UNKNOWN"),
            message=response.get("message", "No response"),
            action=response.get("action", "ASK"),
            tool=response.get("tool"),
            parameters=response.get("parameters"),
            session_id=session_id,
            event_id=event_id,
            event_link=event_link
        )
        
    except Exception as e:
        logger.error(f"SlotBot Error: {e}")
        return ChatResponse(
            state="ERROR",
            message="An error occurred. Please try again.",
            action="ERROR",
            session_id=session_id
        )

@app.post("/ui-chat", response_model=UIChatResponse)
async def ui_chat(req: UIChatRequest):
    """SlotBot UI-Driven State Machine Endpoint"""
    session_id = req.session_id
    
    try:
        # Process message through UI state machine
        response = process_slotbot_ui_message(
            req.message, 
            session_id, 
            req.selected_action, 
            req.selected_date, 
            req.selected_slot
        )
        
        logger.info(f"SlotBot UI Response: {response}")
        
        # Handle tool execution if needed
        event_id = None
        event_link = None
        
        if response.get("action") == "CALL_TOOL" and response.get("tool"):
            tool_name = response.get("tool")
            params = response.get("parameters", {})
            
            if tool_name == "CREATE_MEETING":
                dt = params.get("datetime")
                dur = params.get("duration", 30)
                
                # Use the new create_meeting_tool function
                result = create_meeting_tool(dt, dur)
                
                if result.get("success"):
                    event_id = result.get("event_id")
                    event_link = result.get("event_link")
                    response["message"] = "✅ Meeting scheduled successfully"
                else:
                    response["message"] = f"❌ Failed to create meeting: {result.get('error')}"
                    response["action"] = "ERROR"
        
        return UIChatResponse(
            intent=response.get("intent", ""),
            date=response.get("date", ""),
            selected_slot=response.get("selected_slot", ""),
            message=response.get("message", "No response"),
            action=response.get("action", "ASK"),
            tool=response.get("tool"),
            parameters=response.get("parameters"),
            session_id=session_id,
            event_id=event_id,
            event_link=event_link
        )
        
    except Exception as e:
        logger.error(f"SlotBot UI Error: {e}")
        return UIChatResponse(
            intent="",
            date="",
            selected_slot="",
            message="An error occurred. Please try again.",
            action="ERROR",
            session_id=session_id
        )

class SlotRequest(BaseModel):
    date: str

class SlotResponse(BaseModel):
    available_slots: List[str]
    booked_slots: List[str]

@app.post("/list-available-slots", response_model=SlotResponse)
async def list_slots(req: SlotRequest):
    """List available and booked slots for a given date"""
    try:
        slots = list_available_slots(req.date)
        return SlotResponse(
            available_slots=slots.get("available_slots", []),
            booked_slots=slots.get("booked_slots", [])
        )
    except Exception as e:
        logger.error(f"Error listing slots: {e}")
        return SlotResponse(
            available_slots=[],
            booked_slots=[]
        )

class DirectScheduleRequest(BaseModel):
    date: str
    slot: str
    session_id: str = "default"

@app.post("/direct-schedule", response_model=UIChatResponse)
async def direct_schedule(req: DirectScheduleRequest):
    """Direct scheduling endpoint for Smart Scheduler"""
    try:
        # Convert slot to ISO datetime
        from datetime import datetime
        slot_time = datetime.strptime(req.slot, "%I:%M %p").time()
        date_obj = datetime.fromisoformat(req.date)
        datetime_obj = datetime.combine(date_obj.date(), slot_time)
        datetime_str = f"{datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')}+05:30"
        
        logger.info(f"Direct scheduling: {req.date} {req.slot} -> {datetime_str}")
        
        # Create meeting directly
        result = create_meeting_tool(datetime_str, 30)
        
        if result.get("success"):
            return UIChatResponse(
                intent="SCHEDULE",
                date=req.date,
                selected_slot=req.slot,
                message="✅ Meeting scheduled successfully",
                action="COMPLETE",
                session_id=req.session_id,
                event_id=result.get("event_id"),
                event_link=result.get("event_link")
            )
        else:
            return UIChatResponse(
                intent="SCHEDULE",
                date=req.date,
                selected_slot=req.slot,
                message=f"❌ Failed to create meeting: {result.get('error')}",
                action="ERROR",
                session_id=req.session_id
            )
            
    except Exception as e:
        logger.error(f"Direct schedule error: {e}")
        return UIChatResponse(
            intent="SCHEDULE",
            date=req.date,
            selected_slot=req.slot,
            message="❌ Failed to schedule meeting. Please try again.",
            action="ERROR",
            session_id=req.session_id
        )

@app.get("/health")
async def health():
    return {"status": "ok"}