# OAuth Redirect URI Fix Guide

## The Problem
Error 400: redirect_uri_mismatch means the redirect URI in your code doesn't match what's configured in Google Cloud Console.

## Quick Fix Steps:

### Option 1: Update Google Cloud Console (Recommended)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select your project

2. **Navigate to Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Find your OAuth 2.0 Client ID
   - Click "Edit" (pencil icon)

3. **Add Correct Redirect URI**
   - Scroll to "Authorized redirect URIs"
   - Click "+ ADD URI"
   - Add: `http://localhost:8080/`
   - Click "Save"

### Option 2: Use Different Port (Alternative)

If you can't access Google Cloud Console, I can change the port in the code to match an existing redirect URI.

## Current Configuration:
- **Code uses**: `http://localhost:8080/`
- **Google expects**: Whatever is configured in your OAuth client

## After Fix:
The OAuth flow will work and you can create real Google Calendar events!

## Test Again:
After fixing the redirect URI, run:
```bash
curl -s -X POST http://localhost:8001/chat -H "Content-Type: application/json" -d '{"message": "book meeting for tomorrow at 3pm"}'
```
