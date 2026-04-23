# Real Google Calendar Testing Guide

## 🚀 Test Real Calendar Integration

### Step 1: Test the API
```bash
curl -s -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "book meeting for tomorrow at 3pm"}'
```

### Step 2: OAuth Authorization (First Time Only)
1. **Browser will open automatically** with Google OAuth URL
2. **Sign in** with your Google account (tejas.mokarkar@pinnacle.in)
3. **Click "Allow"** to grant calendar access
4. **Authorization complete** - token.json will be saved

### Step 3: Verify Event Created
After successful API call, check:
1. **Response should contain:**
   ```json
   {
     "message": "Event 'Meeting' created successfully for 2026-04-24 15:00",
     "event_id": "actual_google_event_id",
     "event_link": "https://calendar.google.com/event?id=..."
   }
   ```

2. **Check your Google Calendar:**
   - Visit https://calendar.google.com/
   - Look for the event at the specified time
   - Event should appear in your calendar

### Step 4: Test Different Formats
```bash
# Test tomorrow at 10am
curl -s -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Schedule meeting for tomorrow at 10am"}'

# Test Friday at 2pm
curl -s -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create event for Friday at 2pm"}'

# Test specific datetime
curl -s -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "book meeting for 2026-04-25T14:00:00"}'
```

## 🔍 Verification Checklist

- ✅ API returns success message
- ✅ Event appears in Google Calendar
- ✅ Event has correct time and date
- ✅ Event link works (opens in Google Calendar)
- ✅ Event ID is valid Google Calendar ID

## 🛠 Troubleshooting

**If OAuth fails:**
- Check redirect URI in Google Cloud Console
- Ensure `http://localhost:8080/` is added to authorized URIs

**If event not created:**
- Check server logs for errors
- Verify calendar permissions
- Ensure datetime format is correct
