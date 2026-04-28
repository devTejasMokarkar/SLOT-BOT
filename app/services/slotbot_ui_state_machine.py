#!/usr/bin/env python3
"""
SlotBot UI-Driven State Machine Implementation

This implementation follows the UI-driven scheduling flow:
1. Ask user to select action (Schedule Appointment / Check Availability)
2. For scheduling: ask for date, show slots, ask for slot selection, confirm once, create meeting
3. For availability: ask for date, show slots

Response Format:
{
  "intent": "SCHEDULE|CHECK_AVAILABILITY",
  "date": "YYYY-MM-DD",
  "selected_slot": "HH:MM AM/PM",
  "message": "User-friendly message",
  "action": "ASK|SHOW_SLOTS|CONFIRM|CALL_TOOL|COMPLETE"
}

States:
- INITIAL: Ask for action selection
- WAITING_FOR_DATE: Waiting for user to provide/select date
- SHOWING_SLOTS: Display available/booked slots
- WAITING_FOR_SLOT: Waiting for user to select time slot
- AWAITING_CONFIRMATION: Ask for confirmation once
- CREATING_MEETING: Execute CREATE_MEETING tool
- COMPLETED: Meeting scheduled successfully
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from app.services.calendar_service import list_available_slots, create_meeting_tool

class SlotBotUIStateMachine:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = "INITIAL"
        self.intent = None
        self.selected_date = None
        self.selected_slot = None
        self.slot_data = None
        
    def format_response(self, intent: str, date: str, selected_slot: str, message: str, action: str, tool: str = None, parameters: Dict = None) -> Dict:
        """Format response according to UI-driven specification"""
        response = {
            "intent": intent,
            "date": date or "",
            "selected_slot": selected_slot or "",
            "message": message,
            "action": action
        }
        
        if tool and parameters:
            response["tool"] = tool
            response["parameters"] = parameters
            
        return response
    
    def process_message(self, message: str, selected_action: str = None, selected_date: str = None, selected_slot: str = None) -> Dict:
        """Main state machine processor for UI-driven flow"""
        
        # Handle UI inputs (buttons/selectors) with priority over text
        if selected_action:
            return self._handle_action_selection(selected_action)
        elif selected_date:
            return self._handle_date_selection(selected_date)
        elif selected_slot:
            return self._handle_slot_selection(selected_slot)
        
        # Handle text messages as fallback
        message_lower = message.lower().strip()
        
        if self.state == "INITIAL":
            return self._handle_initial_message(message_lower)
        elif self.state == "WAITING_FOR_DATE":
            return self._handle_date_text_input(message_lower)
        elif self.state == "SHOWING_SLOTS":
            return self._handle_slots_interaction(message_lower)
        elif self.state == "WAITING_FOR_SLOT":
            return self._handle_slot_text_input(message_lower)
        elif self.state == "AWAITING_CONFIRMATION":
            return self._handle_confirmation(message_lower)
        elif self.state == "COMPLETED":
            return self._handle_completed()
        else:
            return self.format_response("", "", "", "Invalid state. Please restart.", "ASK")
    
    def _handle_action_selection(self, action: str) -> Dict:
        """Handle action selection from UI buttons"""
        if action == "schedule_appointment":
            self.intent = "SCHEDULE"
            self.state = "WAITING_FOR_DATE"
            return self.format_response(
                "SCHEDULE", "", "", 
                "Please select a date for your appointment:", 
                "ASK"
            )
        elif action == "check_availability":
            self.intent = "CHECK_AVAILABILITY"
            self.state = "WAITING_FOR_DATE"
            return self.format_response(
                "CHECK_AVAILABILITY", "", "", 
                "Please select a date to check availability:", 
                "ASK"
            )
        else:
            return self.format_response("", "", "", "Please select a valid action.", "ASK")
    
    def _handle_initial_message(self, message: str) -> Dict:
        """Handle initial text message - show action options"""
        if any(keyword in message for keyword in ["schedule", "meeting", "book", "appointment"]):
            self.intent = "SCHEDULE"
            self.state = "WAITING_FOR_DATE"
            return self.format_response(
                "SCHEDULE", "", "", 
                "Please select a date for your appointment:", 
                "ASK"
            )
        elif any(keyword in message for keyword in ["available", "check", "availability", "free"]):
            self.intent = "CHECK_AVAILABILITY"
            self.state = "WAITING_FOR_DATE"
            return self.format_response(
                "CHECK_AVAILABILITY", "", "", 
                "Please select a date to check availability:", 
                "ASK"
            )
        else:
            return self.format_response(
                "", "", "", 
                "What would you like to do?\n\n• Schedule Appointment\n• Check Availability", 
                "ASK"
            )
    
    def _handle_date_selection(self, date_str: str) -> Dict:
        """Handle date selection from UI"""
        try:
            # Validate date format
            datetime.fromisoformat(date_str)
            self.selected_date = date_str
            
            # Fetch slots for the selected date
            self.slot_data = list_available_slots(date_str)
            self.state = "SHOWING_SLOTS"
            
            return self._display_slots()
            
        except ValueError:
            return self.format_response(
                self.intent or "", "", "", 
                "Invalid date format. Please select a valid date.", 
                "ASK"
            )
    
    def _handle_date_text_input(self, message: str) -> Dict:
        """Handle date input via text (fallback)"""
        # Try to extract date from message
        try:
            # Simple date extraction - in production, use more sophisticated parsing
            if "today" in message:
                date_str = datetime.now().strftime("%Y-%m-%d")
            elif "tomorrow" in message:
                date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                # Try to parse YYYY-MM-DD format
                import re
                date_match = re.search(r'\d{4}-\d{2}-\d{2}', message)
                if date_match:
                    date_str = date_match.group()
                else:
                    return self.format_response(
                        self.intent or "", "", "", 
                        "Please select a date using the date picker.", 
                        "ASK"
                    )
            
            return self._handle_date_selection(date_str)
            
        except:
            return self.format_response(
                self.intent or "", "", "", 
                "Please select a date using the date picker.", 
                "ASK"
            )
    
    def _display_slots(self) -> Dict:
        """Display available and booked slots"""
        if not self.slot_data:
            return self.format_response(
                self.intent, self.selected_date, "", 
                "Error fetching slots. Please try again.", 
                "ASK"
            )
        
        available_slots = self.slot_data.get("available_slots", [])
        booked_slots = self.slot_data.get("booked_slots", [])
        
        if self.intent == "CHECK_AVAILABILITY":
            # Just show availability, don't proceed to scheduling
            self.state = "COMPLETED"
            message = self._format_slots_message(available_slots, booked_slots)
            return self.format_response(
                "CHECK_AVAILABILITY", self.selected_date, "", 
                message, 
                "COMPLETE"
            )
        else:
            # Show slots and wait for selection
            self.state = "WAITING_FOR_SLOT"
            message = self._format_slots_message(available_slots, booked_slots)
            return self.format_response(
                "SCHEDULE", self.selected_date, "", 
                message, 
                "SHOW_SLOTS"
            )
    
    def _format_slots_message(self, available_slots: List[str], booked_slots: List[str]) -> str:
        """Format slots message with emoji indicators"""
        message_parts = []
        
        if available_slots:
            message_parts.append("🟢 Available Slots:")
            for slot in available_slots[:10]:  # Limit to first 10 for UI
                message_parts.append(f"- {slot}")
        
        if booked_slots:
            message_parts.append("\n🔴 Booked Slots:")
            for slot in booked_slots[:10]:  # Limit to first 10 for UI
                message_parts.append(f"- {slot}")
        
        if not available_slots and not booked_slots:
            return "No slots found for this date."
        
        return "\n".join(message_parts)
    
    def _handle_slot_selection(self, slot: str) -> Dict:
        """Handle slot selection from UI"""
        if not self.slot_data:
            return self.format_response(
                self.intent, self.selected_date, "", 
                "Slot data not available. Please select a date again.", 
                "ASK"
            )
        
        available_slots = self.slot_data.get("available_slots", [])
        
        # Validate that the selected slot is available
        if slot not in available_slots:
            return self.format_response(
                self.intent, self.selected_date, slot, 
                "This slot is not available. Please select an available slot.", 
                "SHOW_SLOTS"
            )
        
        self.selected_slot = slot
        self.state = "AWAITING_CONFIRMATION"
        
        # Ask for confirmation ONCE - show user-friendly date format
        try:
            date_obj = datetime.fromisoformat(self.selected_date)
            month_name = date_obj.strftime("%B")
            day = date_obj.day
            dt_formatted = f"{slot} on {month_name} {day}"
        except:
            dt_formatted = f"{slot} on {self.selected_date}"
            
        return self.format_response(
            "SCHEDULE", self.selected_date, slot, 
            f"Confirm appointment at {dt_formatted}?", 
            "CONFIRM"
        )
    
    def _handle_slot_text_input(self, message: str) -> Dict:
        """Handle slot input via text (fallback)"""
        if not self.slot_data:
            return self.format_response(
                self.intent, self.selected_date, "", 
                "Please select a date first.", 
                "ASK"
            )
        
        available_slots = self.slot_data.get("available_slots", [])
        
        # Try to match the input with available slots
        message_lower = message.lower()
        matched_slot = None
        
        for slot in available_slots:
            slot_lower = slot.lower()
            if slot_lower in message_lower or message_lower in slot_lower:
                matched_slot = slot
                break
        
        if matched_slot:
            return self._handle_slot_selection(matched_slot)
        else:
            return self.format_response(
                self.intent, self.selected_date, "", 
                "Please select a slot from the available options.", 
                "SHOW_SLOTS"
            )
    
    def _handle_slots_interaction(self, message: str) -> Dict:
        """Handle interaction while showing slots"""
        if any(keyword in message for keyword in ["select", "choose", "book", "schedule"]):
            self.state = "WAITING_FOR_SLOT"
            return self.format_response(
                self.intent, self.selected_date, "", 
                "Please select a time slot from the available options.", 
                "SHOW_SLOTS"
            )
        else:
            # Show slots again
            return self._display_slots()
    
    def _handle_confirmation(self, message: str) -> Dict:
        """Handle user confirmation - ask only ONCE"""
        confirmations = ["yes", "y", "yeah", "yup", "ye3s", "confirm", "proceed"]
        
        if message.lower().strip() in confirmations:
            # User confirmed - immediately create meeting
            self.state = "CREATING_MEETING"
            return self._create_meeting()
        else:
            # User rejected - go back to slot selection
            self.state = "WAITING_FOR_SLOT"
            return self.format_response(
                "SCHEDULE", self.selected_date, "", 
                "Please select a different time slot.", 
                "SHOW_SLOTS"
            )
    
    def _create_meeting(self) -> Dict:
        """Create meeting - preserve exact user-selected time"""
        if not self.selected_date or not self.selected_slot:
            self.state = "COMPLETED"
            return self.format_response(
                "SCHEDULE", self.selected_date, self.selected_slot, 
                "Missing date or slot information. Please start over.", 
                "COMPLETE"
            )
        
        # Convert slot time to datetime string - PRESERVE EXACT TIME
        try:
            # Parse slot like "10:00 AM" or "02:30 PM"
            slot_time = datetime.strptime(self.selected_slot, "%I:%M %p").time()
            
            # Combine with selected date
            date_obj = datetime.fromisoformat(self.selected_date)
            datetime_obj = datetime.combine(date_obj.date(), slot_time)
            
            # CRITICAL: Create ISO format with IST timezone WITHOUT shifting time
            # Format: YYYY-MM-DDTHH:MM:SS+05:30
            datetime_str = f"{datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')}+05:30"
            
            # DEBUG LOG: Show exact conversion
            print(f"DEBUG: Slot selection conversion:")
            print(f"  selected_slot_ui: '{self.selected_slot}'")
            print(f"  selected_date: '{self.selected_date}'")
            print(f"  converted_datetime: '{datetime_str}'")
            print(f"  hour_24: {datetime_obj.hour:02d}")
            print(f"  minute: {datetime_obj.minute:02d}")
            
            # Call CREATE_MEETING tool
            self.state = "COMPLETED"
            
            return self.format_response(
                "SCHEDULE", self.selected_date, self.selected_slot, 
                "Creating meeting...", 
                "CALL_TOOL",
                "CREATE_MEETING",
                {
                    "datetime": datetime_str,
                    "duration": 30
                }
            )
            
        except Exception as e:
            self.state = "COMPLETED"
            return self.format_response(
                "SCHEDULE", self.selected_date, self.selected_slot, 
                f"Error creating meeting: {str(e)}", 
                "COMPLETE"
            )
    
    def _handle_completed(self) -> Dict:
        """Handle completed state"""
        return self.format_response(
            self.intent or "", self.selected_date or "", self.selected_slot or "", 
            "✅ Meeting scheduled successfully. Ready for next request.", 
            "COMPLETE"
        )

# Session management
active_ui_sessions: Dict[str, SlotBotUIStateMachine] = {}

def get_ui_session_machine(session_id: str) -> SlotBotUIStateMachine:
    """Get or create a UI state machine for a session"""
    if session_id not in active_ui_sessions:
        active_ui_sessions[session_id] = SlotBotUIStateMachine(session_id)
    return active_ui_sessions[session_id]

def process_slotbot_ui_message(message: str = "", session_id: str = "default", selected_action: str = None, selected_date: str = None, selected_slot: str = None) -> Dict:
    """Process a message through the SlotBot UI state machine"""
    machine = get_ui_session_machine(session_id)
    return machine.process_message(message, selected_action, selected_date, selected_slot)

def reset_ui_session(session_id: str = "default"):
    """Reset a UI session (for testing or manual reset)"""
    if session_id in active_ui_sessions:
        del active_ui_sessions[session_id]
