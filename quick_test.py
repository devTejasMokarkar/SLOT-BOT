#!/usr/bin/env python3
"""
Quick test for improved SlotBot flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.slotbot_state_machine import SlotBotStateMachine

def test_improved_flow():
    """Test the improved flow based on CLI issues"""
    
    print("=== IMPROVED FLOW TEST ===\n")
    
    machine = SlotBotStateMachine("test")
    
    # Test scenario similar to CLI issue
    print("User: schedule meeting for may 2 2026 5pm")
    response = machine.process_message("schedule meeting for may 2 2026 5pm")
    print(f"Bot: {response['message']}")
    print(f"State: {machine.state}")
    print()
    
    # Test context update with "may 5?"
    print("User: may 5 10am")
    response = machine.process_message("may 5 10am")
    print(f"Bot: {response['message']}")
    print(f"State: {machine.state}")
    print(f"Stored datetime: {machine.stored_datetime}")
    print()
    
    # Test confirmation
    if response.get("action") == "CONFIRM":
        print("User: yes")
        response = machine.process_message("yes")
        print(f"Bot: {response['message']}")
        print(f"Action: {response['action']}")
        print(f"State: {machine.state}")

if __name__ == "__main__":
    test_improved_flow()
