# Contributing to Appointment Agent

Thank you for your interest in contributing to Appointment Agent! This document provides guidelines for contributors.

## 🚀 Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Install** dependencies: `pip install -r requirements.txt`
5. **Set up** environment: `cp .env.example .env` and add your API keys

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Add type hints where appropriate
- Keep functions small and focused

### Testing
- Test new features thoroughly
- Ensure backward compatibility
- Test both mock and real calendar modes
- Verify error handling

### Documentation
- Update README.md for new features
- Add inline comments for complex logic
- Update API documentation

## 🔄 Pull Request Process

1. **Push** to your fork: `git push origin feature/amazing-feature`
2. **Create** Pull Request on GitHub
3. **Describe** your changes clearly
4. **Link** any relevant issues
5. **Wait** for review and feedback

## 🐛 Bug Reports

When reporting bugs, please include:
- **Environment**: Python version, OS
- **Steps to reproduce**: Detailed steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Error messages**: Any error logs

## 💡 Feature Requests

For new features, please provide:
- **Use case**: Why this feature is needed
- **Proposed solution**: How you envision it working
- **Alternatives considered**: Other approaches you thought of

## 📧 Development Setup

### Local Development
```bash
# Clone and setup
git clone https://github.com/your-username/SlotMan.git
cd SlotMan
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your API keys to .env

# Run tests
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Code Structure
```
appointment-agent/
├── app/
│   ├── main.py              # FastAPI application
│   └── services/
│       ├── ai_service.py      # OpenAI integration
│       ├── calendar_service.py # Google Calendar API
│       ├── mock_calendar_service.py # Mock calendar for testing
│       └── simple_parser.py  # Fallback parser
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt          # Python dependencies
├── Dockerfile              # Container configuration
└── README.md               # Project documentation
```

## 🎯 Contributing Areas

We welcome contributions in:
- **AI Integration**: Better intent extraction, new AI providers
- **Calendar Features**: Recurring events, multiple calendars
- **Error Handling**: Better fallback mechanisms
- **Documentation**: Improved guides and examples
- **Testing**: Unit tests, integration tests
- **Performance**: Optimization, caching

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🤝 Code of Conduct

Please be respectful and professional in all interactions. We're here to build great software together!

---

Thank you for contributing to Appointment Agent! 🎯
