#!/usr/bin/env python3
"""
SlotBot State Machine Implementation

CRITICAL RULES:
1. CONFIRM ONLY WHEN DATA IS COMPLETE
   - Must have both date and time
   - If missing → Ask for specific field
   - DO NOT ask for confirmation

2. CONTEXT LOCK RULE (VERY IMPORTANT)
   - Once user provides date and time → STORE it internally
   - ALWAYS reuse it
   - If user says "yes" → Use stored datetime
   - DO NOT ask for context again

3. NO CONFIRMATION LOOP
   - Once confirmed → STOP asking
   - STOP checking availability again
   - IMMEDIATELY proceed to CREATE_MEETING

4. FALLBACK RULE
   - If user says "yes" but no datetime exists
   - Respond: "Please provide date and time for the meeting."

States:
1. COLLECTING_DETAILS
2. CHECKING_AVAILABILITY  
3. AWAITING_CONFIRMATION
4. CONFIRMED
5. COMPLETED

Transitions (MANDATORY):
- If slot is FREE: → Move to AWAITING_CONFIRMATION
- If user says "yes" in AWAITING_CONFIRMATION: → Move to CONFIRMED → IMMEDIATELY CALL CREATE_MEETING → Move to COMPLETED
- Once COMPLETED: → NEVER ask again → Respond with success

Confirmation handling treats these as YES:
- yes, y, yeah, yup, ye3s (typo), confirm, proceed
"""

import json
import re
from datetime import datetime
from typing import Dict, Optional, List
from app.services.ai_service import get_ai_response
from app.services.calendar_service import create_calendar_event, check_availability

class SlotBotStateMachine:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.state = "COLLECTING_DETAILS"
        self.stored_datetime = None
        self.stored_duration = 30
        self.last_response = None
        
    def is_confirmation(self, message: str) -> bool:
        """Check if message is a confirmation"""
        confirmations = ["yes", "y", "yeah", "yup", "ye3s", "confirm", "proceed"]
        return message.lower().strip() in confirmations
    
    def has_complete_datetime(self, datetime_str: str) -> bool:
        """Check if datetime has both date and time"""
        if not datetime_str or datetime_str == "null":
            return False
        try:
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            # Check if it's a date-only (midnight) or has actual time
            return dt.hour != 0 or dt.minute != 0 or dt.second != 0
        except:
            return False
    
    def format_response(self, message: str, action: str, tool: str = None, parameters: Dict = None, datetime_str: str = None) -> Dict:
        """Format response according to specification"""
        response = {
            "intent": "SCHEDULE",
            "datetime": datetime_str or self.stored_datetime or "",
            "message": message,
            "action": action,
            "tool": tool,
            "parameters": parameters or {}
        }
        self.last_response = response
        return response
    
    def process_message(self, message: str) -> Dict:
        """Main state machine processor"""
        
        # Check if this is a new scheduling request and we're in COMPLETED state
        message_lower = message.lower()
        is_new_scheduling = any(keyword in message_lower for keyword in ["schedule", "meeting", "book", "appointment"])
        
        if self.state == "COMPLETED" and is_new_scheduling:
            # Reset state for new scheduling request
            self.state = "COLLECTING_DETAILS"
            self.stored_datetime = None
            self.stored_duration = 30
        
        if self.state == "COLLECTING_DETAILS":
            return self._handle_collecting_details(message)
        
        elif self.state == "CHECKING_AVAILABILITY":
            return self._handle_checking_availability()
        
        elif self.state == "AWAITING_CONFIRMATION":
            return self._handle_awaiting_confirmation(message)
        
        elif self.state == "CONFIRMED":
            return self._handle_confirmed()
        
        elif self.state == "COMPLETED":
            return self._handle_completed()
        
        else:
            return self.format_response("Invalid state. Please restart.", "ASK")
    
    def _handle_collecting_details(self, message: str) -> Dict:
        """Handle initial message collection and intent extraction"""
        
        # Clear stale context if this looks like a fresh scheduling request
        message_lower = message.lower()
        is_fresh_request = any(keyword in message_lower for keyword in ["schedule", "meeting", "book", "appointment"])
        
        if is_fresh_request and self.stored_datetime:
            # Fresh scheduling request - clear previous context
            self.stored_datetime = None
            self.stored_duration = 30
        
        # CONTEXT LOCK: If we already have stored datetime and user is providing time/changes
        if self.stored_datetime and (":" in message_lower or "am" in message_lower or "pm" in message_lower or any(month in message_lower for month in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])):
            # User is providing time/date modification, update stored datetime
            ai_response = get_ai_response([{"role": "user", "content": f"Schedule meeting {message}"}])
            
            # Check for AI service errors
            if ai_response.get("action") == "ERROR":
                # Propagate AI service errors (like authentication issues)
                return self.format_response(
                    ai_response.get("message"),
                    "ERROR",
                    None, None, None
                )
            
            new_dt = ai_response.get("datetime")
            if new_dt and new_dt != "null":
                self.stored_datetime = new_dt
                self.stored_duration = ai_response.get("duration_minutes", 30)
                # Move to availability check
                self.state = "CHECKING_AVAILABILITY"
                return self._handle_checking_availability()
        
        # Get AI response to extract intent and datetime
        ai_response = get_ai_response([{"role": "user", "content": message}])
        
        # Check for AI service errors
        if ai_response.get("action") == "ERROR":
            # Propagate AI service errors (like authentication issues)
            return self.format_response(
                ai_response.get("message"),
                "ERROR",
                None, None, None
            )
        
        intent = ai_response.get("intent", "UNKNOWN")
        extracted_dt = ai_response.get("datetime")
        
        if intent != "SCHEDULE" or not extracted_dt or extracted_dt == "null":
            # Handle non-scheduling intents or missing datetime
            if ai_response.get("action") in ["CALL_TOOL"] and ai_response.get("tool") in ["LIST_MEETINGS", "SUGGEST_SLOTS"]:
                # Check if this might be a scheduling attempt with missing time
                message_lower = message.lower()
                if any(keyword in message_lower for keyword in ["schedule", "meeting", "meet", "book", "appointment"]) and ("?" in message or any(month in message_lower for month in ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])):
                    # This looks like a scheduling attempt, ask for missing info
                    return self.format_response(
                        "I can help you schedule. What time would you like?",
                        "ASK",
                        None, None, extracted_dt
                    )
                # Pass through genuine check/list requests
                return self.format_response(
                    ai_response.get("message"),
                    "CALL_TOOL",
                    ai_response.get("tool"),
                    ai_response.get("parameters", {}),
                    extracted_dt
                )
            else:
                # Ask for specific missing information
                if not extracted_dt or extracted_dt == "null":
                    return self.format_response(
                        "Please provide date and time for the meeting.",
                        "ASK",
                        None, None, extracted_dt
                    )
                else:
                    return self.format_response(
                        ai_response.get("message", "I can help you schedule meetings."),
                        ai_response.get("action", "ASK"),
                        None, None, extracted_dt
                    )
        
        # CONTEXT LOCK RULE: Store the extracted datetime and duration
        self.stored_datetime = extracted_dt
        self.stored_duration = ai_response.get("duration_minutes", 30)
        
        # CONFIRM ONLY WHEN DATA IS COMPLETE: Check if we have complete datetime
        if not self.has_complete_datetime(extracted_dt):
            # Ask for missing time component
            return self.format_response(
                "I have the date, but what time would you like to schedule?",
                "ASK",
                None, None, extracted_dt
            )
        
        # Check if AI is asking for confirmation (e.g., outside office hours)
        if ai_response.get("action") == "REJECT":
            return self.format_response(
                ai_response.get("message"),
                ai_response.get("action"),
                None, None, extracted_dt
            )
        
        # Additional validation: Check if date is too far in the future (beyond 1 year)
        if extracted_dt:
            try:
                from datetime import datetime
                meeting_date = datetime.fromisoformat(extracted_dt.replace('Z', '+00:00'))
                current_date = datetime.now()
                years_ahead = (meeting_date.year - current_date.year)
                if years_ahead > 1 or (years_ahead == 1 and meeting_date.month > current_date.month):
                    return self.format_response(
                        "I cannot schedule meetings more than a year in advance. Please choose a date within the next year.",
                        "REJECT",
                        None, None, extracted_dt
                    )
            except:
                pass  # If date parsing fails, continue with normal flow
        
        # If AI asks but it's within office hours, proceed to availability check
        if ai_response.get("action") == "ASK":
            # Check if this is a confirmation request about office hours
            msg = ai_response.get("message", "").lower()
            if "office hours" in msg or "proceed" in msg:
                # This is a confirmation request, move to availability check first
                self.state = "CHECKING_AVAILABILITY"
                return self._handle_checking_availability()
            else:
                # This is asking for more info, pass through
                return self.format_response(
                    ai_response.get("message"),
                    ai_response.get("action"),
                    None, None, extracted_dt
                )
        
        # Move to checking availability
        self.state = "CHECKING_AVAILABILITY"
        return self._handle_checking_availability()
    
    def _handle_checking_availability(self) -> Dict:
        """Check availability for the stored datetime"""
        if not self.stored_datetime:
            self.state = "COLLECTING_DETAILS"
            return self.format_response("Please provide date and time for the meeting.", "ASK")
        
        # Check availability
        available = check_availability(self.stored_datetime, self.stored_duration)
        
        if available:
            # Slot is free - move to confirmation
            self.state = "AWAITING_CONFIRMATION"
            dt_formatted = datetime.fromisoformat(self.stored_datetime).strftime('%I:%M %p on %B %d, %Y')
            return self.format_response(
                f"Slot available at {dt_formatted}. Confirm?",
                "CONFIRM"
            )
        else:
            # Slot is busy - reset to collecting details but keep context
            self.state = "COLLECTING_DETAILS"
            # CONTEXT LOCK: Keep stored datetime for reuse
            return self.format_response(
                "Slot is busy. Please choose a different time.",
                "ASK"
            )
    
    def _handle_awaiting_confirmation(self, message: str) -> Dict:
        """Handle user confirmation"""
        if self.is_confirmation(message):
            # User confirmed - move to confirmed state
            self.state = "CONFIRMED"
            return self._handle_confirmed()
        else:
            # User didn't confirm - go back to collecting details but keep context
            self.state = "COLLECTING_DETAILS"
            # CONTEXT LOCK: Keep stored datetime for reuse
            return self.format_response(
                "Let's try again. Would you like a different time?",
                "ASK"
            )
    
    def _handle_confirmed(self) -> Dict:
        """Immediately create meeting after confirmation - NO RECHECKING AVAILABILITY"""
        if not self.stored_datetime:
            # FALLBACK RULE: If user says "yes" but no datetime exists
            self.state = "COLLECTING_DETAILS"
            return self.format_response(
                "Please provide date and time for the meeting.",
                "ASK"
            )
        
        # CRITICAL: IMMEDIATELY CALL CREATE_MEETING without re-checking availability
        self.state = "COMPLETED"
        
        return self.format_response(
            "Creating meeting...",
            "CALL_TOOL",
            "CREATE_MEETING",
            {
                "datetime": self.stored_datetime,
                "duration": self.stored_duration
            }
        )
    
    def _handle_completed(self) -> Dict:
        """Handle completed state - don't reset here, let process_message handle it"""
        return self.format_response(
            "✅ Meeting scheduled successfully. Ready for next request.",
            "COMPLETE"
        )

# Session management
active_sessions: Dict[str, SlotBotStateMachine] = {}

def get_session_machine(session_id: str) -> SlotBotStateMachine:
    """Get or create a state machine for a session"""
    if session_id not in active_sessions:
        active_sessions[session_id] = SlotBotStateMachine(session_id)
    return active_sessions[session_id]

def process_slotbot_message(message: str, session_id: str = "default") -> Dict:
    """Process a message through the SlotBot state machine"""
    machine = get_session_machine(session_id)
    return machine.process_message(message)

def reset_session(session_id: str = "default"):
    """Reset a session (for testing or manual reset)"""
    if session_id in active_sessions:
        del active_sessions[session_id]
