#!/usr/bin/env python3
"""
Test improved flow with better validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.slotbot_state_machine import process_slotbot_message

def test_improved_flow():
    """Test improved flow with validation"""
    
    print("=== IMPROVED FLOW TEST WITH VALIDATION ===\n")
    
    # Test 1: Valid date (should work)
    print("Test 1: Valid date (May 1, 2026)")
    response1 = process_slotbot_message("schedule meeting for 1 may 2026 time 5 pm", "test1")
    print(f"Response: {response1['message']}")
    print(f"Action: {response1['action']}")
    
    if response1.get("action") == "CONFIRM":
        response2 = process_slotbot_message("yes", "test1")
        print(f"After confirmation: {response2['message']}")
        print(f"Final action: {response2['action']}")
    print()
    
    # Test 2: Invalid date (May 2027 - should be rejected)
    print("Test 2: Invalid date (May 2027)")
    response3 = process_slotbot_message("schedule meeting for 5 may 2027 at time 5 pm", "test2")
    print(f"Response: {response3['message']}")
    print(f"Action: {response3['action']}")
    print()
    
    # Test 3: Try to confirm invalid date (should fail)
    print("Test 3: Try to confirm invalid date")
    response4 = process_slotbot_message("yes", "test2")
    print(f"Response: {response4['message']}")
    print(f"Action: {response4['action']}")

if __name__ == "__main__":
    test_improved_flow()
