#!/usr/bin/env python3
"""
Simple test for SlotBot basic functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.slotbot_state_machine import SlotBotStateMachine, reset_session

def test_basic_flow():
    """Test basic SlotBot flow step by step"""
    
    print("=== SlotBot Basic Flow Test ===\n")
    
    # Create a new session
    machine = SlotBotStateMachine("test_session")
    
    # Step 1: User provides complete datetime
    print("Step 1: User says 'schedule meeting 29 April 2026 5pm'")
    response = machine.process_message("schedule meeting 29 April 2026 5pm")
    print(f"State: {machine.state}")
    print(f"Response: {response}")
    print(f"Stored datetime: {machine.stored_datetime}")
    print()
    
    # Step 2: Check what happens next
    if response.get("action") == "CONFIRM":
        print("Step 2: User confirms with 'yes'")
        response = machine.process_message("yes")
        print(f"State: {machine.state}")
        print(f"Response: {response}")
        print(f"Stored datetime: {machine.stored_datetime}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_basic_flow()
