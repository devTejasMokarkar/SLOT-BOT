import React, { useState, useEffect } from 'react';
import { Bot, Calendar, MessageCircle, CheckCircle, XCircle } from 'lucide-react';
import ChatMode from './components/ChatMode';
import SchedulerMode from './components/SchedulerMode';
import ModeToggle from './components/ModeToggle';
import { apiService } from './services/api';

function App() {
  const [mode, setMode] = useState('chat'); // 'chat' | 'scheduler'
  const [error, setError] = useState(null);

  useEffect(() => {
    // Test API connection on mount
    const testConnection = async () => {
      try {
        await apiService.health();
        setError(null);
      } catch (err) {
        setError('Failed to connect to SlotBot backend. Please ensure the server is running on port 8001.');
      }
    };
    testConnection();
  }, []);

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setError(null);
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
        <div className="card max-w-md w-full p-6 text-center">
          <XCircle className="w-12 h-12 text-error-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Connection Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-primary-600 p-2 rounded-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">SlotBot</h1>
                <p className="text-xs text-gray-500">AI Scheduling Assistant</p>
              </div>
            </div>
            
            <ModeToggle mode={mode} onModeChange={handleModeChange} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Left Panel - Mode Description */}
          <div className="lg:col-span-1">
            <div className="card p-6 sticky top-8">
              <div className="flex items-center space-x-3 mb-4">
                {mode === 'chat' ? (
                  <>
                    <MessageCircle className="w-6 h-6 text-primary-600" />
                    <h2 className="text-lg font-semibold text-gray-900">Chat Mode</h2>
                  </>
                ) : (
                  <>
                    <Calendar className="w-6 h-6 text-primary-600" />
                    <h2 className="text-lg font-semibold text-gray-900">Smart Scheduler</h2>
                  </>
                )}
              </div>
              
              {mode === 'chat' ? (
                <div className="space-y-3 text-sm text-gray-600">
                  <p>• Natural language conversation</p>
                  <p>• Type your scheduling requests</p>
                  <p>• AI handles the details</p>
                  <p>• Multi-turn dialogue support</p>
                  <div className="mt-4 p-3 bg-primary-50 rounded-lg">
                    <p className="text-xs font-medium text-primary-800 mb-2">Example:</p>
                    <p className="text-xs text-primary-700">"Schedule meeting for tomorrow at 3pm"</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 text-sm text-gray-600">
                  <p>• Visual scheduling interface</p>
                  <p>• Calendar date picker</p>
                  <p>• Time slot selection</p>
                  <p>• Quick 3-step booking</p>
                  <div className="mt-4 p-3 bg-primary-50 rounded-lg">
                    <p className="text-xs font-medium text-primary-800 mb-2">Benefits:</p>
                    <p className="text-xs text-primary-700">No typing required • Visual availability • Fast booking</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Active Mode */}
          <div className="lg:col-span-2">
            <div className="animate-fade-in">
              {mode === 'chat' ? (
                <ChatMode />
              ) : (
                <SchedulerMode />
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-success-500" />
              <span>Powered by PINNACLE AI</span>
            </div>
            <div className="flex items-center space-x-4">
              <span>© 2026 SlotBot</span>
              <span>•</span>
              <span>Smart Scheduling Assistant</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
