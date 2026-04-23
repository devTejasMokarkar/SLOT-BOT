import json
from datetime import datetime, timedelta
from typing import Dict, List

# Simple in-memory calendar for testing
class MockCalendar:
    def __init__(self):
        self.events: List[Dict] = []
        self.event_id_counter = 1
    
    def create_event(self, start_time: str, summary: str = "Meeting", duration_minutes: int = 30) -> Dict:
        """Create a mock calendar event"""
        try:
            start_datetime = datetime.fromisoformat(start_time)
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            event = {
                'id': f'mock_event_{self.event_id_counter}',
                'summary': summary,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'htmlLink': f'https://mock-calendar.com/event/{self.event_id_counter}',
                'created': datetime.now().isoformat()
            }
            
            self.events.append(event)
            self.event_id_counter += 1
            
            return {
                'success': True,
                'event_id': event['id'],
                'event_link': event['htmlLink'],
                'message': f"Mock event '{summary}' created successfully for {start_datetime.strftime('%Y-%m-%d %H:%M')}",
                'event': event
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Mock calendar error: {e}",
                'message': "Failed to create mock calendar event"
            }
    
    def list_events(self) -> List[Dict]:
        """List all mock events"""
        return self.events
    
    def clear_events(self):
        """Clear all mock events"""
        self.events = []
        self.event_id_counter = 1

# Global mock calendar instance
mock_calendar = MockCalendar()

def create_mock_calendar_event(start_time: str, summary: str = "Meeting", duration_minutes: int = 30) -> Dict:
    """Mock function that mimics create_calendar_event"""
    return mock_calendar.create_event(start_time, summary, duration_minutes)

def get_mock_events() -> List[Dict]:
    """Get all mock events"""
    return mock_calendar.list_events()

def clear_mock_events():
    """Clear all mock events"""
    mock_calendar.clear_events()
