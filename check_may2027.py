#!/usr/bin/env python3
"""
Check if May 2027 meeting was actually created
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.calendar_service import list_meetings, create_calendar_event

def check_may2027():
    """Check May 2027 meetings"""
    
    print("=== CHECKING MAY 2027 MEETINGS ===\n")
    
    # Check May 5, 2027
    print("📅 Meetings for 2027-05-05:")
    meetings = list_meetings("2027-05-05")
    print(f"   {meetings}")
    print()
    
    # Test direct creation for May 2027
    print("🧪 Testing direct May 2027 meeting creation:")
    result = create_calendar_event("2027-05-05T17:00:00", "May 2027 Test", 30)
    print(f"   Result: {result}")
    print()
    
    # Check if it was created
    print("📋 Meetings for 2027-05-05 after creation:")
    meetings = list_meetings("2027-05-05")
    print(f"   {meetings}")

if __name__ == "__main__":
    check_may2027()
