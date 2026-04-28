import React from 'react';
import { MessageCircle, Calendar } from 'lucide-react';

const ModeToggle = ({ mode, onModeChange }) => {
  return (
    <div className="flex items-center bg-gray-100 rounded-lg p-1">
      <button
        onClick={() => onModeChange('chat')}
        className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
          mode === 'chat'
            ? 'bg-white text-primary-600 shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        <MessageCircle className="w-4 h-4" />
        <span>Chat with SlotBot</span>
      </button>
      
      <button
        onClick={() => onModeChange('scheduler')}
        className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
          mode === 'scheduler'
            ? 'bg-white text-primary-600 shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        <Calendar className="w-4 h-4" />
        <span>Smart Scheduler</span>
      </button>
    </div>
  );
};

export default ModeToggle;
