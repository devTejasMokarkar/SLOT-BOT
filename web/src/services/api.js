const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async health() {
    return this.request('/health');
  }

  // Chat mode endpoints
  async chat(message, sessionId = 'default_user') {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    });
  }

  // UI mode endpoints
  async uiChat(data) {
    return this.request('/ui-chat', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Available slots endpoint
  async listAvailableSlots(date) {
    return this.request('/list-available-slots', {
      method: 'POST',
      body: JSON.stringify({ date }),
    });
  }

  // Utility method to convert time slot to ISO format
  slotToIso(date, timeSlot) {
    // Convert "09:00 AM" format to 24-hour format
    const [time, period] = timeSlot.split(' ');
    let [hours, minutes] = time.split(':');
    
    hours = parseInt(hours);
    if (period === 'PM' && hours !== 12) {
      hours += 12;
    } else if (period === 'AM' && hours === 12) {
      hours = 0;
    }
    
    const isoString = `${date}T${hours.toString().padStart(2, '0')}:${minutes}:00+05:30`;
    return isoString;
  }

  // Utility method to format date for API
  formatDateForApi(date) {
    return date.toISOString().split('T')[0];
  }

  // Utility method to format time for display
  formatTimeForDisplay(timeSlot) {
    return timeSlot;
  }
}

export const apiService = new ApiService();
