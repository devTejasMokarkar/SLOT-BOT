#!/usr/bin/env python3
"""
Test SlotBot flow with May 2027 date
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.slotbot_state_machine import SlotBotStateMachine

def test_may2027_flow():
    """Test SlotBot with May 2027 date"""
    
    print("=== MAY 2027 SLOTBOT FLOW TEST ===\n")
    
    machine = SlotBotStateMachine("test_may2027")
    
    # Test May 5, 2027 5 PM
    print("User: schedule meeting for 5 may 2027 at time 5 pm")
    response = machine.process_message("schedule meeting for 5 may 2027 at time 5 pm")
    print(f"Bot: {response['message']}")
    print(f"State: {machine.state}")
    print(f"Stored datetime: {machine.stored_datetime}")
    print(f"Action: {response['action']}")
    print()
    
    # If it asks for confirmation, confirm it
    if response.get("action") == "CONFIRM":
        print("User: yes")
        response = machine.process_message("yes")
        print(f"Bot: {response['message']}")
        print(f"State: {machine.state}")
        print(f"Action: {response['action']}")
        print(f"Tool: {response.get('tool')}")
        print(f"Parameters: {response.get('parameters')}")
        
        # If it calls CREATE_MEETING, let's test the actual calendar creation
        if response.get("tool") == "CREATE_MEETING":
            print("\n🔍 Testing actual calendar creation:")
            from app.services.calendar_service import create_calendar_event
            dt = response.get("parameters", {}).get("datetime")
            result = create_calendar_event(dt, "Meeting", 30)
            print(f"   Calendar result: {result}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_may2027_flow()
