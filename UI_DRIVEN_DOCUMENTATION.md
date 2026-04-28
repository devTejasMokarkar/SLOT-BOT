# SlotBot UI-Driven Scheduling System

## Overview

SlotBot has been transformed from a text-based scheduling assistant to a **UI-driven system** that provides a seamless, intuitive scheduling experience. The system prioritizes button and selector interactions over free text input, following strict UX rules for maximum efficiency.

## Core Architecture

### New Components

1. **`slotbot_ui_state_machine.py`** - UI-driven state machine
2. **`list_available_slots()`** - Calendar service function for slot fetching
3. **`create_meeting_tool()`** - Tool wrapper for meeting creation
4. **`/ui-chat` endpoint** - New API endpoint for UI interactions

### Response Format

All responses follow this standardized format:

```json
{
  "intent": "SCHEDULE|CHECK_AVAILABILITY",
  "date": "YYYY-MM-DD",
  "selected_slot": "HH:MM AM/PM",
  "message": "User-friendly message",
  "action": "ASK|SHOW_SLOTS|CONFIRM|CALL_TOOL|COMPLETE",
  "tool": "CREATE_MEETING",
  "parameters": {"datetime": "ISO_STRING", "duration": 30},
  "session_id": "user_session",
  "event_id": "calendar_event_id",
  "event_link": "calendar_event_url"
}
```

## Primary Flow

### STEP 1: Action Selection

The system starts by asking the user to select an action:

**Options:**
- `Schedule Appointment`
- `Check Availability`

**UI Implementation:** Use buttons/radio buttons, not text input.

### IF USER SELECTS "Schedule Appointment":

#### STEP 2: Date Selection
- Ask user to select date (prefer date picker UI)
- Accept both UI selection and text fallback ("today", "tomorrow", "YYYY-MM-DD")

#### STEP 3: Fetch and Display Slots
- Call `LIST_AVAILABLE_SLOTS(date)` tool
- Display structured response:

```json
{
  "available_slots": ["10:00 AM", "11:30 AM", "03:00 PM"],
  "booked_slots": ["12:00 PM", "01:00 PM"]
}
```

**UI Display Format:**
```
🟢 Available Slots:
- 10:00 AM
- 11:30 AM
- 03:00 PM

🔴 Booked Slots:
- 12:00 PM
- 01:00 PM
```

#### STEP 4: Slot Selection
- Ask user to select time slot from available options
- **NEVER** ask user to type time manually
- Use clickable buttons/selectors for available slots

#### STEP 5: Confirmation (ONCE ONLY)
- Validate selected slot again
- Ask for confirmation: `"Confirm appointment at [TIME] on [DATE]?"`
- **CRITICAL:** Ask confirmation ONLY ONCE

#### STEP 6: Meeting Creation
- If user confirms → Immediately call `CREATE_MEETING` tool
- Respond with success message and event details
- **NO RECHECKING AVAILABILITY** after confirmation

### IF USER SELECTS "Check Availability":

#### STEP 2: Date Selection
- Ask for date selection
- Use date picker UI

#### STEP 3: Display Availability
- Call `LIST_AVAILABLE_SLOTS(date)`
- Show available vs booked slots
- **DO NOT** proceed to scheduling

## State Machine Flow

```
INITIAL → Ask for action selection
    ↓
WAITING_FOR_DATE → Ask for date
    ↓
SHOWING_SLOTS → Display available/booked slots
    ↓ (for scheduling)
WAITING_FOR_SLOT → Ask for slot selection
    ↓
AWAITING_CONFIRMATION → Ask confirmation ONCE
    ↓
CREATING_MEETING → Execute CREATE_MEETING
    ↓
COMPLETED → Success message
```

## API Endpoints

### New UI-Driven Endpoint

**POST** `/ui-chat`

**Request Body:**
```json
{
  "message": "optional_text_fallback",
  "session_id": "user_session",
  "selected_action": "schedule_appointment|check_availability",
  "selected_date": "YYYY-MM-DD",
  "selected_slot": "HH:MM AM/PM"
}
```

**Response:** Standardized format with all fields

### Legacy Endpoint (Still Available)

**POST** `/chat` - Original text-based flow

## UX Rules (STRICT)

1. **Prefer UI Controls:** Always use buttons/selectors over text input
2. **No Manual Typing:** NEVER ask user to type date/time if UI selection available
3. **Clear Slot Display:** Always show available vs booked slots with emoji indicators
4. **Minimal Inputs:** Complete scheduling in 2-3 steps maximum
5. **Single Confirmation:** Ask confirmation ONLY once, then execute immediately
6. **No Conversational Loops:** Avoid back-and-forth, keep flow linear

## Error Handling

### No Available Slots
```
🔴 All slots are booked for this date.
Would you like to try tomorrow?
```

### Slot Becomes Unavailable
```
❌ This slot is no longer available.
Please select a different time slot.
```

### Invalid Date
```
❌ Invalid date format.
Please select a date using the date picker.
```

## Implementation Details

### Calendar Integration

The `list_available_slots()` function:
- Generates standard slots (9 AM - 6 PM, 30-min intervals)
- Fetches existing events from Google Calendar
- Returns available vs booked slots structure
- Handles errors gracefully with default slots

### Time Zone Handling

- All times stored in IST (UTC+5:30)
- Slot times formatted as "HH:MM AM/PM" for UI
- ISO format used for internal datetime storage
- Automatic timezone conversion for calendar API

### Session Management

- Each user session maintains independent state
- Sessions persist across multiple interactions
- Manual session reset available for testing
- Automatic cleanup on completion

## Testing

### Test Script

Run the comprehensive test suite:

```bash
python test_ui_flow.py
```

### Test Cases Covered

1. **Complete Schedule Appointment Flow**
   - Action selection → Date → Slot → Confirmation → Creation
   
2. **Check Availability Flow**
   - Action selection → Date → Display slots
   
3. **Text Input Fallback**
   - Natural language → Date parsing → Slot selection

### Manual Testing

Use curl or API client to test the `/ui-chat` endpoint:

```bash
# Start flow
curl -X POST http://localhost:8000/ui-chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test"}'

# Select action
curl -X POST http://localhost:8000/ui-chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "selected_action": "schedule_appointment"}'

# Select date
curl -X POST http://localhost:8000/ui-chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "selected_date": "2026-04-29"}'

# Select slot
curl -X POST http://localhost:8000/ui-chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "selected_slot": "10:00 AM"}'

# Confirm
curl -X POST http://localhost:8000/ui-chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "yes"}'
```

## Migration Guide

### From Text-Based to UI-Driven

1. **Frontend Changes:**
   - Replace text inputs with UI controls
   - Implement date picker component
   - Create slot selection buttons
   - Add action selection buttons

2. **API Changes:**
   - Use `/ui-chat` endpoint instead of `/chat`
   - Send structured parameters instead of free text
   - Handle new response format

3. **State Management:**
   - Track UI state separately from text state
   - Handle button clicks vs text input
   - Implement proper error states

## Benefits

1. **Faster Scheduling:** 2-3 steps vs 5-10 steps in text-based
2. **Better UX:** Clear visual indicators and controls
3. **Fewer Errors:** No parsing mistakes from free text
4. **Mobile Friendly:** Touch-optimized interface
5. **Consistent Experience:** Predictable flow every time

## Future Enhancements

1. **Recurring Meetings:** Support for weekly/monthly appointments
2. **Multiple Calendars:** Support for work/personal calendar separation
3. **Meeting Types:** Different durations and purposes
4. **Time Zone Detection:** Automatic user timezone detection
5. **Smart Suggestions:** AI-powered optimal time recommendations

---

**SlotBot UI-Driven System: Transforming scheduling from conversation to interaction.**
