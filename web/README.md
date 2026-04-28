# SlotBot Web Application

A modern browser-based scheduling assistant with dual interaction modes - Chat and Smart Scheduler.

## Features

### 🤖 Chat Mode
- Natural language conversation interface
- AI-powered scheduling assistance
- Multi-turn dialogue support
- Real-time responses

### 📅 Smart Scheduler Mode
- Visual scheduling interface
- Calendar date picker
- Time slot selection
- Quick 3-step booking process
- No typing required

## Technology Stack

- **Frontend**: React 18
- **Styling**: TailwindCSS
- **Icons**: Lucide React
- **Backend**: FastAPI (Python)
- **Calendar Integration**: Google Calendar API

## Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Google Calendar API credentials

### Backend Setup

1. Navigate to the project root:
```bash
cd /home/ptspl03/AI/slotbot
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Start the backend server:
```bash
source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Setup

1. Navigate to the web directory:
```bash
cd web
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open your browser and navigate to:
```
http://localhost:3000
```

## API Endpoints

### Chat Mode
- `POST /chat` - Send chat messages to SlotBot
- `GET /health` - Health check endpoint

### Smart Scheduler Mode
- `POST /ui-chat` - UI-driven scheduling
- `POST /list-available-slots` - Get available slots for a date

## Usage

### Chat Mode
1. Toggle to "Chat with SlotBot" mode
2. Type natural language requests like:
   - "Schedule meeting for tomorrow at 3pm"
   - "Check my appointments for Friday"
   - "Cancel meeting at 2pm"

### Smart Scheduler Mode
1. Toggle to "Smart Scheduler" mode
2. Select type (Appointment/Meeting)
3. Choose action (View Slots/Schedule)
4. Pick date from calendar
5. Select available time slot
6. Confirm booking

## Configuration

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API key for AI processing
- `USE_MOCK_CALENDAR` - Set to false for real Google Calendar integration

### Google Calendar Setup
1. Create Google Cloud Project
2. Enable Google Calendar API
3. Create OAuth 2.0 Credentials
4. Download `credentials.json` to project root
5. Configure redirect URIs for localhost

## Development

### Project Structure
```
web/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── ChatMode.js
│   │   ├── SchedulerMode.js
│   │   └── ModeToggle.js
│   ├── services/
│   │   └── api.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
├── tailwind.config.js
└── README.md
```

### Build for Production
```bash
npm run build
```

### Testing
```bash
npm test
```

## Troubleshooting

### Common Issues

1. **Backend Connection Error**
   - Ensure backend server is running on port 8001
   - Check CORS configuration in FastAPI

2. **Google Calendar Authentication**
   - Verify `credentials.json` is in project root
   - Check OAuth consent screen configuration
   - Ensure redirect URIs match localhost

3. **TailwindCSS Not Working**
   - Ensure PostCSS is configured correctly
   - Check that TailwindCSS dependencies are installed

4. **Date/Time Issues**
   - Verify timezone configuration (IST +05:30)
   - Check ISO format conversion in API calls

## License

MIT License - see main project LICENSE file for details.
