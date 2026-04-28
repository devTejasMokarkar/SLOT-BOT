import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';

const ChatMode = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m SlotBot, your AI scheduling assistant. How can I help you schedule meetings today?'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `user_${Date.now()}`);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await apiService.chat(inputMessage.trim(), sessionId);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.message || 'I processed your request.',
        eventLink: response.event_link,
        eventId: response.event_id
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, I encountered an error. Please try again later.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="card h-[600px] flex flex-col">
      {/* Chat Header */}
      <div className="border-b border-gray-100 p-4 bg-gradient-to-r from-primary-50 to-primary-100">
        <div className="flex items-center space-x-3">
          <Bot className="w-5 h-5 text-primary-600" />
          <h3 className="font-semibold text-gray-900">Chat with SlotBot</h3>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start space-x-3 ${
              message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
            }`}
          >
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
              message.type === 'bot' ? 'bg-primary-600' : 'bg-gray-600'
            }`}>
              {message.type === 'bot' ? (
                <Bot className="w-4 h-4 text-white" />
              ) : (
                <User className="w-4 h-4 text-white" />
              )}
            </div>
            
            <div className={`max-w-xs lg:max-w-md ${
              message.type === 'user' ? 'text-right' : ''
            }`}>
              <div className={`inline-block px-4 py-2 rounded-lg text-sm ${
                message.type === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}>
                {message.content}
              </div>
              
              {message.eventLink && (
                <div className="mt-2">
                  <a
                    href={message.eventLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-primary-600 hover:text-primary-800 underline"
                  >
                    View Calendar Event →
                  </a>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <Loader2 className="w-4 h-4 text-gray-600 animate-spin" />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="border-t border-gray-100 p-4">
        <div className="flex space-x-3">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span>Send</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatMode;
