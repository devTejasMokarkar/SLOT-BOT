#!/usr/bin/env python3
"""
Test December 2026 date processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.slotbot_state_machine import SlotBotStateMachine

def test_december2026():
    """Test December 2026 date processing"""
    
    print("=== DECEMBER 2026 TEST ===\n")
    
    machine = SlotBotStateMachine("test_dec")
    
    # Test December 5, 2026 12 PM
    print("User: schedule meeting for december 5 2026 at time 12 pm")
    response = machine.process_message("schedule meeting for december 5 2026 at time 12 pm")
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
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_december2026()
