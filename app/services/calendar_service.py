import os
import json
from datetime import datetime, timedelta
from typing import List
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
            flow.run_local_server(port=8080, access_type='offline', prompt='consent')
            creds = flow.credentials
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)

def create_calendar_event(start_time, summary="Meeting", duration_minutes=30):
    try:
        service = get_calendar_service()
        
        # Handle None duration
        if duration_minutes is None:
            duration_minutes = 30
            
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
        
        event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
        
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
        
        # Handle None duration
        if duration_minutes is None:
            duration_minutes = 30
            
        start_datetime = datetime.fromisoformat(start_time)
        if start_datetime.tzinfo is None:
            from datetime import timezone
            ist = timezone(timedelta(hours=5, minutes=30))
            start_datetime = start_datetime.replace(tzinfo=ist)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        body = {
            "timeMin": start_datetime.isoformat(),
            "timeMax": end_datetime.isoformat(),
            "items": [{"id": "primary"}]
        }
        
        freebusy_result = service.freebusy().query(body=body).execute()
        busy_slots = freebusy_result.get('calendars', {}).get('primary', {}).get('busy', [])
        
        return len(busy_slots) == 0
        
    except Exception as e:
        print(f"Calendar Availability Error: {e}")
        # If calendar service is unavailable, assume the slot is available
        # rather than incorrectly marking it as busy
        return True

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

def list_available_slots(date_str: str):
    """
    Fetch available and booked slots for a given date
    Returns structured data with available_slots and booked_slots lists
    """
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
        
        # Generate standard time slots (9 AM to 6 PM, 30-minute intervals)
        all_slots = []
        current_time = start_datetime.replace(hour=9, minute=0, second=0, microsecond=0)
        end_of_day = start_datetime.replace(hour=18, minute=0, second=0, microsecond=0)
        
        while current_time < end_of_day:
            slot_time = current_time.strftime('%I:%M %p')
            all_slots.append(slot_time)
            current_time += timedelta(minutes=30)
        
        # Extract booked slots from existing events
        booked_slots = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if 'T' in start:  # It's a datetime event
                event_time = datetime.fromisoformat(start)
                slot_time = event_time.strftime('%I:%M %p')
                booked_slots.append(slot_time)
        
        # Available slots are those not in booked_slots
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return {
            "available_slots": available_slots,
            "booked_slots": booked_slots
        }
        
    except Exception as e:
        print(f"Error fetching slots: {e}")
        # Return default slots on error
        default_slots = ["09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM", 
                        "12:00 PM", "12:30 PM", "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM",
                        "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM"]
        return {
            "available_slots": default_slots,
            "booked_slots": []
        }

def create_meeting_tool(datetime_str: str, duration_minutes: int = 30):
    """
    Tool function for creating meetings - wrapper around create_calendar_event
    """
    result = create_calendar_event(datetime_str, "Meeting", duration_minutes)
    
    if result['success']:
        return {
            "success": True,
            "message": result['message'],
            "event_id": result['event_id'],
            "event_link": result['event_link']
        }
    else:
        return {
            "success": False,
            "message": result['message'],
            "error": result['error']
        }

def create_meeting_with_attendees(datetime_str: str, title: str = "Meeting", attendees: List[str] = None, duration_minutes: int = 30):
    """
    Create meeting with custom title and attendees
    """
    if attendees is None:
        attendees = []
    
    try:
        service = get_calendar_service()
        
        # Handle None duration
        if duration_minutes is None:
            duration_minutes = 30
            
        start_datetime = datetime.fromisoformat(datetime_str)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        event = {
            'summary': title,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'IST',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'IST',
            },
        }
        
        # Add attendees if provided
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        event = service.events().insert(calendarId='primary', body=event, sendUpdates='all').execute()
        
        return {
            'success': True,
            'event_id': event['id'],
            'event_link': event['htmlLink'],
            'message': f"Event '{title}' created successfully for {start_datetime.strftime('%Y-%m-%d %H:%M')}"
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