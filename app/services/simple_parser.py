import re
from datetime import datetime, timedelta
from typing import Dict, Optional

def extract_intent_simple(user_message: str) -> Dict:
    """Simple rule-based intent extraction when AI APIs are unavailable"""
    
    message_lower = user_message.lower()
    
    # Check intent
    intent = "UNKNOWN"
    if any(word in message_lower for word in ["create", "schedule", "book", "meeting", "event", "appointment", "add"]):
        intent = "CREATE_EVENT"
    
    if intent == "UNKNOWN":
        return {
            "intent": "UNKNOWN",
            "datetime": None,
            "duration_minutes": 0,
            "confidence": 0.0
        }
    
    # Extract datetime
    datetime_str = None
    
    # Today
    if "today" in message_lower:
        time_match = re.search(r'(\d{1,2})(:\d{2})?\s*(am|pm)', message_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            
            if period == "pm" and hour != 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
                
            today = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            datetime_str = today.isoformat()
    
    # Tomorrow
    elif "tomorrow" in message_lower:
        time_match = re.search(r'(\d{1,2})(:\d{2})?\s*(am|pm)', message_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            
            if period == "pm" and hour != 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
                
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            datetime_str = tomorrow.isoformat()
    
    # Friday
    elif "friday" in message_lower:
        time_match = re.search(r'(\d{1,2})(:\d{2})?\s*(am|pm)', message_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            period = time_match.group(3)
            
            if period == "pm" and hour != 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
                
            # Find next Friday
            today = datetime.now()
            days_until_friday = (4 - today.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            friday = today + timedelta(days=days_until_friday)
            friday = friday.replace(hour=hour, minute=minute, second=0, microsecond=0)
            datetime_str = friday.isoformat()
    
    # ISO datetime pattern
    iso_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', user_message)
    if iso_match and not datetime_str:
        datetime_str = iso_match.group(0)
    
    return {
        "intent": intent,
        "datetime": datetime_str,
        "duration_minutes": 30,
        "confidence": 0.8 if datetime_str else 0.3
    }
