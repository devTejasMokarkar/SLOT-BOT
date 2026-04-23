import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from app.services.ai_service import extract_intent
from app.services.simple_parser import extract_intent_simple
from app.services.calendar_service import create_calendar_event
from app.services.mock_calendar_service import create_mock_calendar_event

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Appointment Agent API",
    description="Intelligent appointment scheduling with Google Calendar integration",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    event_id: str = None
    event_link: str = None

class ErrorResponse(BaseModel):
    error: str
    detail: str = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Appointment Agent API",
        "version": "1.0.0",
        "description": "Intelligent appointment scheduling with Google Calendar integration",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2026-04-23T18:00:00Z"}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Process user message and create calendar event"""
    try:
        logger.info(f"Incoming request: {req.message}")

        # Try AI service first, fallback to simple parser if it fails or returns unknown
        try:
            data = extract_intent(req.message)
            logger.info(f"AI response: {data}")
            
            # Check for quota issues
            if "quota" in str(data).lower() or "429" in str(data) or data.get("error"):
                logger.warning("AI quota exceeded, using simple parser")
                data = extract_intent_simple(req.message)
                logger.info(f"Simple parser response: {data}")
            # If AI service returns unknown intent, fallback to simple parser
            elif data.get("intent") == "UNKNOWN" or not data.get("datetime"):
                logger.warning("AI returned unknown, using simple parser")
                data = extract_intent_simple(req.message)
                logger.info(f"Simple parser response: {data}")
        except Exception as e:
            logger.error(f"AI service failed: {e}, using simple parser")
            data = extract_intent_simple(req.message)
            logger.info(f"Simple parser response: {data}")

        logger.info(f"Detected intent: {data.get('intent')}")
        if data.get("intent") != "CREATE_EVENT":
            return ChatResponse(message="I can help you book meetings. Try again.")

        start_time = data.get("datetime")
        duration = data.get("duration_minutes", 30)

        if not start_time:
            raise HTTPException(status_code=400, detail="Please provide a valid time.")

        # Use mock calendar if environment variable is set (no Google API needed)
        use_mock = os.environ.get("USE_MOCK_CALENDAR", "false").lower() == "true"
        
        if use_mock:
            result = create_mock_calendar_event(start_time, "Meeting", duration)
        else:
            result = create_calendar_event(start_time, "Meeting", duration)

        if result["success"]:
            return ChatResponse(
                message=result["message"],
                event_id=result["event_id"],
                event_link=result["event_link"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])

    except HTTPException as he:
        logger.error(f"HTTP error: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")