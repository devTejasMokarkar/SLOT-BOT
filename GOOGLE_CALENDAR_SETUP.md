# Google Calendar API Setup Guide

To enable autonomous calendar event creation, you need to set up Google Cloud credentials:

## Steps:

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Calendar API**
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client ID"
   - Select "Desktop app" as application type
   - Name it "Appointment Agent"
   - **Important**: Add this redirect URI: `http://localhost:8080/`
   - Click "Create"

4. **Download Credentials**
   - Download the JSON file
   - Rename it to `credentials.json`
   - Place it in the project root directory (`/home/ptspl03/AI/appointment-agent/`)

5. **First-time Authentication**
   - When you first run the app, it will open a browser window
   - Sign in with your Google account
   - Grant permission to access your calendar
   - This will create a `token.json` file for future use

## Files Created:
- `credentials.json` - OAuth client credentials (you provide this)
- `token.json` - User authentication token (auto-generated)

## Security Notes:
- Never commit `credentials.json` or `token.json` to version control
- Add them to `.gitignore` file
- Keep your credentials secure and private
