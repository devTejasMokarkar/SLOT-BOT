#!/usr/bin/env python3
"""
Check recent meetings in Google Calendar
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.calendar_service import list_meetings
from datetime import datetime, timedelta

def check_recent_meetings():
    """Check meetings for recent dates"""
    
    print("=== CHECKING RECENT MEETINGS IN GOOGLE CALENDAR ===\n")
    
    # Check dates you mentioned in CLI
    dates_to_check = [
        "2026-04-30",  # April 30
        "2026-05-01",  # May 1
        "2026-05-05",  # May 5
    ]
    
    for date_str in dates_to_check:
        print(f"📅 Meetings for {date_str}:")
        meetings = list_meetings(date_str)
        print(f"   {meetings}")
        print()
    
    print("If you see meetings listed above, they were successfully created in your Google Calendar!")
    print("Check your Google Calendar at: https://calendar.google.com")

if __name__ == "__main__":
    check_recent_meetings()
