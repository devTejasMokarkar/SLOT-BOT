#!/usr/bin/env python3
"""
Check June 2026 meetings in Google Calendar
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.calendar_service import list_meetings

def check_june_meetings():
    """Check meetings for June 2026"""
    
    print("=== CHECKING JUNE 2026 MEETINGS IN GOOGLE CALENDAR ===\n")
    
    # Check June 1, 2026
    print("📅 Meetings for 2026-06-01:")
    meetings = list_meetings("2026-06-01")
    print(f"   {meetings}")
    print()
    
    # Also test creating a June meeting directly
    print("🧪 Testing direct June meeting creation:")
    from app.services.calendar_service import create_calendar_event
    result = create_calendar_event("2026-06-01T12:00:00", "June Test Meeting", 30)
    print(f"   Result: {result}")
    print()
    
    print("If you see meetings listed above, they were successfully created in your Google Calendar!")
    print("Check your Google Calendar at: https://calendar.google.com")

if __name__ == "__main__":
    check_june_meetings()
