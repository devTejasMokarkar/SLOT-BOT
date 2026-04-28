#!/usr/bin/env python3
"""
Debug availability checking for June 2026
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.calendar_service import check_availability, list_meetings

def debug_availability():
    """Debug availability checking"""
    
    print("=== DEBUGGING AVAILABILITY FOR JUNE 2026 ===\n")
    
    # Test June 1, 2026 12 PM
    datetime_str = "2026-06-01T12:00:00"
    print(f"🔍 Checking availability for: {datetime_str}")
    
    available = check_availability(datetime_str)
    print(f"Available: {available}")
    print()
    
    # Check what meetings exist on that day
    date_str = "2026-06-01"
    print(f"📋 Meetings for {date_str}:")
    meetings = list_meetings(date_str)
    print(f"   {meetings}")
    print()
    
    # Also check surrounding times to see if there's a timezone issue
    times_to_check = [
        "2026-06-01T11:00:00",
        "2026-06-01T12:00:00", 
        "2026-06-01T13:00:00",
        "2026-06-01T12:30:00"
    ]
    
    print("🕐 Checking surrounding times:")
    for time_str in times_to_check:
        available = check_availability(time_str)
        print(f"   {time_str}: {'✅ Available' if available else '❌ Busy'}")

if __name__ == "__main__":
    debug_availability()
