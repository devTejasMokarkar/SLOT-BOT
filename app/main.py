import os
from fastapi import FastAPI
from pydantic import BaseModel
from app.services.ai_service import extract_intent
from app.services.simple_parser import extract_intent_simple
from app.services.calendar_service import create_calendar_event
from app.services.mock_calendar_service import create_mock_calendar_event

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        print("Incoming request:", req.message)

        # Try AI service first, fallback to simple parser if it fails or returns unknown
        try:
            data = extract_intent(req.message)
            print("AI response:", data)
            
            # Check for quota issues
            if "quota" in str(data).lower() or "429" in str(data) or data.get("error"):
                print("AI quota exceeded, using simple parser")
                data = extract_intent_simple(req.message)
                print("Simple parser response:", data)
            # If AI service returns unknown intent, fallback to simple parser
            elif data.get("intent") == "UNKNOWN" or not data.get("datetime"):
                print("AI returned unknown, using simple parser")
                data = extract_intent_simple(req.message)
                print("Simple parser response:", data)
        except Exception as e:
            print(f"AI service failed: {e}, using simple parser")
            data = extract_intent_simple(req.message)
            print("Simple parser response:", data)

        print(f"Detected intent: {data.get('intent')}")
        if data.get("intent") != "CREATE_EVENT":
            return {"message": "I can help you book meetings. Try again."}

        start_time = data.get("datetime")
        duration = data.get("duration_minutes", 30)

        if not start_time:
            return {"message": "Please provide a valid time."}

        # Use mock calendar if environment variable is set (no Google API needed)
        use_mock = os.environ.get("USE_MOCK_CALENDAR", "false").lower() == "true"
        
        if use_mock:
            result = create_mock_calendar_event(start_time, "Meeting", duration)
        else:
            result = create_calendar_event(start_time, "Meeting", duration)

        if result["success"]:
            return {
                "message": result["message"],
                "event_id": result["event_id"],
                "event_link": result["event_link"]
            }
        else:
            return {
                "message": result["message"],
                "error": result["error"]
            }

    except Exception as e:
        print("ERROR:", e)
        return {"message": "Something went wrong"}