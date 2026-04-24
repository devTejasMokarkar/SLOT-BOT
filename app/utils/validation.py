import json
import os
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Python 3.8 fallback
    from datetime import timezone, timedelta
    class ZoneInfo(timezone):
        def __new__(cls, key):
            # simple fallback for IST
            if key == "Asia/Kolkata":
                return timezone(timedelta(hours=5, minutes=30))
            return timezone.utc

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'office_hours.json')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def validate_meeting_request(dt_str: str) -> dict:
    if not dt_str:
        return {"valid": False, "reason": "No datetime provided.", "action": "ASK", "is_past": False, "is_weekend": False, "is_office_hours": False}
        
    config = load_config()
    tz = ZoneInfo(config["timezone"])
    
    try:
        # Assuming ISO format like 2026-04-24T19:30:00
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz)
        else:
            dt = dt.astimezone(tz)
    except ValueError:
        return {"valid": False, "reason": "Invalid datetime format.", "action": "ASK", "is_past": False, "is_weekend": False, "is_office_hours": False}

    now = datetime.now(tz)
    
    is_date_only = len(dt_str.strip()) == 10 and "T" not in dt_str.upper()
    
    is_past = dt.date() < now.date() if is_date_only else dt < now
    is_weekend = dt.weekday() not in config["working_days"]
    
    start_hour, start_minute = map(int, config["work_start_time"].split(':'))
    end_hour, end_minute = map(int, config["work_end_time"].split(':'))
    
    start_time = dt.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    end_time = dt.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
    
    is_office_hours = True if is_date_only else (start_time <= dt <= end_time)
    
    if is_past:
        return {
            "valid": False, 
            "reason": "Cannot schedule in the past.", 
            "action": "REJECT",
            "is_past": True, 
            "is_weekend": is_weekend, 
            "is_office_hours": is_office_hours
        }
        
    if is_weekend:
        return {
            "valid": False, 
            "reason": "Office is closed on weekends.", 
            "action": "REJECT",
            "is_past": False, 
            "is_weekend": True, 
            "is_office_hours": is_office_hours
        }
        
    if not is_office_hours:
        return {
            "valid": False, 
            "reason": "This time is outside office hours. Do you want to proceed anyway?", 
            "action": "ASK",
            "is_past": False, 
            "is_weekend": False, 
            "is_office_hours": False
        }
        
    return {
        "valid": True,
        "reason": "Valid time slot.",
        "action": "SUCCESS",
        "is_past": False,
        "is_weekend": False,
        "is_office_hours": True
    }
