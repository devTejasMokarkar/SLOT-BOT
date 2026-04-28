#!/usr/bin/env python3
"""
Test Google Calendar integration directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.calendar_service import create_calendar_event, check_availability, list_meetings

def test_calendar_integration():
    """Test if Google Calendar is working"""
    
    print("=== GOOGLE CALENDAR INTEGRATION TEST ===\n")
    
    # Test 1: Check availability
    print("Test 1: Checking availability for tomorrow 10am")
    tomorrow = "2026-04-30T10:00:00"
    available = check_availability(tomorrow)
    print(f"Available: {available}")
    print()
    
    # Test 2: List meetings
    print("Test 2: Listing meetings for tomorrow")
    meetings = list_meetings("2026-04-30")
    print(f"Meetings: {meetings}")
    print()
    
    # Test 3: Create a test event
    print("Test 3: Creating a test event")
    result = create_calendar_event("2026-04-30T11:00:00", "Test Meeting", 30)
    print(f"Result: {result}")
    print()
    
    if result.get('success'):
        print("✅ Google Calendar integration is working!")
        print(f"Event ID: {result.get('event_id')}")
        print(f"Event Link: {result.get('event_link')}")
    else:
        print("❌ Google Calendar integration failed!")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    test_calendar_integration()
