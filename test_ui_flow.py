#!/usr/bin/env python3
"""
Test script for SlotBot UI-Driven Flow

This script demonstrates the complete UI-driven scheduling flow:
1. Initial state - asks for action selection
2. Schedule Appointment flow
3. Check Availability flow
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.slotbot_ui_state_machine import process_slotbot_ui_message, reset_ui_session

def print_response(response):
    """Pretty print response"""
    print(f"Intent: {response['intent']}")
    print(f"Date: {response['date']}")
    print(f"Selected Slot: {response['selected_slot']}")
    print(f"Message: {response['message']}")
    print(f"Action: {response['action']}")
    if 'tool' in response:
        print(f"Tool: {response['tool']}")
        print(f"Parameters: {response['parameters']}")
    print("-" * 50)

def test_schedule_appointment_flow():
    """Test the complete schedule appointment flow"""
    print("=== TESTING SCHEDULE APPOINTMENT FLOW ===")
    
    # Reset session
    reset_ui_session("test_session")
    
    # Step 1: Initial state
    print("\n1. Initial State:")
    response = process_slotbot_ui_message(session_id="test_session")
    print_response(response)
    
    # Step 2: Select action
    print("\n2. Select Schedule Appointment:")
    response = process_slotbot_ui_message(
        session_id="test_session", 
        selected_action="schedule_appointment"
    )
    print_response(response)
    
    # Step 3: Select date
    print("\n3. Select Date:")
    response = process_slotbot_ui_message(
        session_id="test_session", 
        selected_date="2026-04-29"
    )
    print_response(response)
    
    # Step 4: Select slot
    print("\n4. Select Time Slot:")
    response = process_slotbot_ui_message(
        session_id="test_session", 
        selected_slot="10:00 AM"
    )
    print_response(response)
    
    # Step 5: Confirm
    print("\n5. Confirm Appointment:")
    response = process_slotbot_ui_message(
        message="yes", 
        session_id="test_session"
    )
    print_response(response)

def test_check_availability_flow():
    """Test the check availability flow"""
    print("\n=== TESTING CHECK AVAILABILITY FLOW ===")
    
    # Reset session
    reset_ui_session("test_session2")
    
    # Step 1: Initial state
    print("\n1. Initial State:")
    response = process_slotbot_ui_message(session_id="test_session2")
    print_response(response)
    
    # Step 2: Select action
    print("\n2. Select Check Availability:")
    response = process_slotbot_ui_message(
        session_id="test_session2", 
        selected_action="check_availability"
    )
    print_response(response)
    
    # Step 3: Select date
    print("\n3. Select Date:")
    response = process_slotbot_ui_message(
        session_id="test_session2", 
        selected_date="2026-04-29"
    )
    print_response(response)

def test_text_fallback():
    """Test text input fallback"""
    print("\n=== TESTING TEXT FALLBACK ===")
    
    # Reset session
    reset_ui_session("test_session3")
    
    # Step 1: Text input for scheduling
    print("\n1. Text Input - Schedule Meeting:")
    response = process_slotbot_ui_message(
        message="I want to schedule a meeting", 
        session_id="test_session3"
    )
    print_response(response)
    
    # Step 2: Text input for date
    print("\n2. Text Input - Today:")
    response = process_slotbot_ui_message(
        message="today", 
        session_id="test_session3"
    )
    print_response(response)

if __name__ == "__main__":
    print("SlotBot UI-Driven Flow Test")
    print("=" * 50)
    
    try:
        test_schedule_appointment_flow()
        test_check_availability_flow()
        test_text_fallback()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
