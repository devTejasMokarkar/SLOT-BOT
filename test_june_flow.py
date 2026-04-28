#!/usr/bin/env python3
"""
Test SlotBot flow with June 2026 date
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.slotbot_state_machine import SlotBotStateMachine

def test_june_flow():
    """Test SlotBot with June 2026 date"""
    
    print("=== JUNE 2026 SLOTBOT FLOW TEST ===\n")
    
    machine = SlotBotStateMachine("test_june")
    
    # Test June 1, 2026 12 PM
    print("User: schedule meeting for 1 june 2026 time 12 pm")
    response = machine.process_message("schedule meeting for 1 june 2026 time 12 pm")
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
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_june_flow()
