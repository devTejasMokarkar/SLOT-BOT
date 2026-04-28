#!/usr/bin/env python3
"""
Test script for SlotBot State Machine
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.slotbot_state_machine import process_slotbot_message, reset_session

def test_slotbot_flow():
    """Test the complete SlotBot flow with various scenarios"""
    
    print("=== SlotBot State Machine Test ===\n")
    
    # Test 1: Complete datetime flow
    print("Test 1: Complete datetime flow")
    print("User: schedule meeting 29 April 2026 5pm")
    response1 = process_slotbot_message("schedule meeting 29 April 2026 5pm", "test1")
    print(f"Bot: {response1}")
    
    print("\nUser: yes")
    response2 = process_slotbot_message("yes", "test1")
    print(f"Bot: {response2}")
    
    reset_session("test1")
    print("\n" + "="*50 + "\n")
    
    # Test 2: Incomplete data - only date
    print("Test 2: Incomplete data - only date")
    print("User: schedule meeting April 29")
    response3 = process_slotbot_message("schedule meeting April 29", "test2")
    print(f"Bot: {response3}")
    
    print("\nUser: 5pm")
    response4 = process_slotbot_message("5pm", "test2")
    print(f"Bot: {response4}")
    
    print("\nUser: yes")
    response5 = process_slotbot_message("yes", "test2")
    print(f"Bot: {response5}")
    
    reset_session("test2")
    print("\n" + "="*50 + "\n")
    
    # Test 3: Context lock test
    print("Test 3: Context lock test")
    print("User: schedule meeting tomorrow 3pm")
    response6 = process_slotbot_message("schedule meeting tomorrow 3pm", "test3")
    print(f"Bot: {response6}")
    
    print("\nUser: no")
    response7 = process_slotbot_message("no", "test3")
    print(f"Bot: {response7}")
    
    print("\nUser: 4pm")
    response8 = process_slotbot_message("4pm", "test3")
    print(f"Bot: {response8}")
    
    print("\nUser: yes")
    response9 = process_slotbot_message("yes", "test3")
    print(f"Bot: {response9}")
    
    reset_session("test3")
    print("\n" + "="*50 + "\n")
    
    # Test 4: Fallback rule - yes without datetime
    print("Test 4: Fallback rule - yes without datetime")
    print("User: yes")
    response10 = process_slotbot_message("yes", "test4")
    print(f"Bot: {response10}")
    
    reset_session("test4")
    print("\n" + "="*50 + "\n")
    
    # Test 5: Various confirmation formats
    print("Test 5: Various confirmation formats")
    print("User: schedule meeting today 6pm")
    response11 = process_slotbot_message("schedule meeting today 6pm", "test5")
    print(f"Bot: {response11}")
    
    confirmations = ["y", "yeah", "yup", "confirm", "proceed"]
    for conf in confirmations:
        reset_session("test5")
        print(f"\nUser: {conf}")
        response = process_slotbot_message(conf, "test5")
        print(f"Bot: {response}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_slotbot_flow()
