#!/usr/bin/env python3
"""
Check available slots for June 2026
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.calendar_service import suggest_slots, check_availability

def check_june_slots():
    """Check available slots for June 2026"""
    
    print("=== CHECKING AVAILABLE SLOTS FOR JUNE 2026 ===\n")
    
    # Get suggested slots for June 1st
    print("📅 Suggested slots for June 1, 2026:")
    slots = suggest_slots("2026-06-01")
    print(f"   {slots}")
    print()
    
    # Check common business hours
    common_times = [
        "2026-06-01T09:00:00",
        "2026-06-01T10:00:00", 
        "2026-06-01T11:00:00",
        "2026-06-01T13:00:00",
        "2026-06-01T14:00:00",
        "2026-06-01T15:00:00",
        "2026-06-01T16:00:00",
        "2026-06-01T17:00:00"
    ]
    
    print("🕐 Checking common business hours:")
    available_slots = []
    for time_str in common_times:
        available = check_availability(time_str)
        status = "✅ Available" if available else "❌ Busy"
        print(f"   {time_str.split('T')[1][:5]}: {status}")
        if available:
            available_slots.append(time_str)
    
    print(f"\n✅ Available slots for June 1, 2026:")
    for slot in available_slots:
        time_str = slot.split('T')[1][:5]
        print(f"   {time_str}")

if __name__ == "__main__":
    check_june_slots()
