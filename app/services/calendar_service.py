import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_calendar_service():
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Credentials file '{CREDENTIALS_FILE}' not found. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def create_calendar_event(start_time, summary="Meeting", duration_minutes=30):
    try:
        service = get_calendar_service()
        
        start_datetime = datetime.fromisoformat(start_time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'IST',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'IST',
            },
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            'success': True,
            'event_id': event['id'],
            'event_link': event['htmlLink'],
            'message': f"Event '{summary}' created successfully for {start_datetime.strftime('%Y-%m-%d %H:%M')}"
        }
        
    except HttpError as e:
        return {
            'success': False,
            'error': f"Calendar API error: {e}",
            'message': "Failed to create calendar event"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {e}",
            'message': "Failed to create calendar event"
        }

def check_availability(start_time: str, duration_minutes: int = 30):
    try:
        service = get_calendar_service()
        
        start_datetime = datetime.fromisoformat(start_time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        body = {
            "timeMin": start_datetime.isoformat() + "Z",
            "timeMax": end_datetime.isoformat() + "Z",
            "items": [{"id": "primary"}]
        }
        
        freebusy_result = service.freebusy().query(body=body).execute()
        busy_slots = freebusy_result.get('calendars', {}).get('primary', {}).get('busy', [])
        
        return len(busy_slots) == 0
        
    except Exception as e:
        print(f"Calendar Availability Error: {e}")
        return False

def suggest_slots(date_str: str):
    # Just suggest 10 AM, 2 PM, 4 PM for simplicity
    base_slots = ["10:00:00", "14:00:00", "16:00:00"]
    suggestions = []
    for slot in base_slots:
        dt_str = f"{date_str}T{slot}"
        if check_availability(dt_str):
            suggestions.append(dt_str)
    return suggestions

def generate_booking_link(start_time):
    # Keep this for backward compatibility
    dt = datetime.fromisoformat(start_time)
    date = dt.date()
    time = dt.strftime("%H:%M")
    USERNAME = "tejas-mokarkar-peflct"
    EVENT = "30min"
    return f"https://cal.com/{USERNAME}/{EVENT}?date={date}&time={time}"

def list_meetings(date_str: str):
    try:
        service = get_calendar_service()
        
        # Parse the date and ensure we span the whole day in IST
        start_datetime = datetime.fromisoformat(f"{date_str}T00:00:00+05:30")
        end_datetime = start_datetime + timedelta(days=1)
        
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=start_datetime.isoformat(), 
            timeMax=end_datetime.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No meetings found for this date."
            
        summary_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            time_str = datetime.fromisoformat(start).strftime('%I:%M %p') if 'T' in start else "All day"
            summary_list.append(f"[{event['id']}] {time_str} - {event.get('summary', 'Busy')}")
            
        return "\n".join(summary_list)
        
    except Exception as e:
        return f"Error fetching meetings: {e}"

def cancel_meeting(event_id: str):
    try:
        service = get_calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return "SUCCESS: Meeting cancelled."
    except HttpError as e:
        if e.resp.status == 404:
            return "ERROR: Meeting not found."
        return f"ERROR: Calendar API error: {e}"
    except Exception as e:
        return f"ERROR: Unexpected error: {e}"