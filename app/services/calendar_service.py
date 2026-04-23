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

def generate_booking_link(start_time):
    # Keep this for backward compatibility
    dt = datetime.fromisoformat(start_time)
    date = dt.date()
    time = dt.strftime("%H:%M")
    USERNAME = "tejas-mokarkar-peflct"
    EVENT = "30min"
    return f"https://cal.com/{USERNAME}/{EVENT}?date={date}&time={time}"