import React from 'react';
import { Loader2 } from 'lucide-react';

const TypingIndicator = ({ statusMessage = "SlotBot is typing..." }) => {
  return (
    <div className="flex items-start space-x-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
        <div className="w-4 h-4">
          <svg viewBox="0 0 24 24" fill="white" className="animate-pulse">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </div>
      </div>
      <div className="bg-gray-100 rounded-lg px-4 py-3 max-w-xs lg:max-w-md">
        <div className="flex items-center space-x-1">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-2 italic">{statusMessage}</div>
      </div>
    </div>
  );
};

export default TypingIndicator;
