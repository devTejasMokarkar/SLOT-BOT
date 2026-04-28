import React, { useState } from 'react';
import { Calendar, Clock, CheckCircle, XCircle, Loader2, Users, CalendarDays, Plus, X } from 'lucide-react';
import { apiService } from '../services/api';

const SchedulerMode = () => {
  const [step, setStep] = useState(1); // 1: Type selection, 2: Date selection, 3: Slot selection, 4: Confirmation
  const [type, setType] = useState(''); // 'meeting'
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedSlot, setSelectedSlot] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [bookedSlots, setBookedSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [eventLink, setEventLink] = useState('');
  const [participants, setParticipants] = useState([]);
  const [emailInput, setEmailInput] = useState('');

  // Get today's date in YYYY-MM-DD format for min date
  const today = new Date().toISOString().split('T')[0];

  const fetchSlots = async (date) => {
    setLoading(true);
    setError('');
    try {
      const response = await apiService.listAvailableSlots(date);
      setAvailableSlots(response.available_slots || []);
      setBookedSlots(response.booked_slots || []);
    } catch (err) {
      setError('Failed to fetch available slots. Please try again.');
      setAvailableSlots([]);
      setBookedSlots([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (date) => {
    setSelectedDate(date);
    setSelectedSlot('');
    if (date) {
      fetchSlots(date);
      setStep(3); // Automatically move to slot selection
    }
  };

  const handleSlotSelect = (slot) => {
    if (bookedSlots.includes(slot)) {
      return; // Don't allow selection of booked slots
    }
    setSelectedSlot(slot);
  };

  const addParticipant = () => {
    const email = emailInput.trim();
    if (email && isValidEmail(email) && !participants.includes(email)) {
      setParticipants([...participants, email]);
      setEmailInput('');
    }
  };

  const removeParticipant = (email) => {
    setParticipants(participants.filter(p => p !== email));
  };

  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleEmailKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addParticipant();
    }
  };

  const handleSchedule = async () => {
    if (!selectedDate || !selectedSlot) return;

    setLoading(true);
    setError('');

    try {
      const sessionId = `scheduler_${Date.now()}`;
      
      // Use direct scheduling endpoint
      const response = await apiService.directSchedule(selectedDate, selectedSlot, sessionId, 'Meeting', participants);

      if (response.event_link) {
        setEventLink(response.event_link);
        setStep(4); // Success step
      } else {
        setError(response.message || 'Failed to schedule meeting. Please try again.');
      }
    } catch (err) {
      setError('Failed to schedule meeting. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetScheduler = () => {
    setStep(1);
    setType('');
    setSelectedDate('');
    setSelectedSlot('');
    setAvailableSlots([]);
    setBookedSlots([]);
    setError('');
    setEventLink('');
    setParticipants([]);
    setEmailInput('');
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Schedule a Meeting</h3>
        <p className="text-sm text-gray-600">Select a date and time for your meeting</p>
      </div>
      
      <div className="grid grid-cols-1 gap-4">
        <button
          onClick={() => {
            setType('meeting');
            setStep(2);
          }}
          className="card p-6 hover:shadow-lg transition-shadow duration-200 text-left group"
        >
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 p-3 rounded-lg group-hover:bg-green-200 transition-colors">
              <Users className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">Meeting</h4>
              <p className="text-sm text-gray-600">Schedule your meeting</p>
            </div>
          </div>
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Select Date</h3>
        <p className="text-sm text-gray-600">Choose your preferred date for your meeting</p>
      </div>

      <div className="card p-6">
        <label htmlFor="date-picker" className="block text-sm font-medium text-gray-700 mb-2">
          <Calendar className="inline w-4 h-4 mr-2" />
          Select Date
        </label>
        <input
          id="date-picker"
          type="date"
          value={selectedDate || today}
          onChange={(e) => handleDateChange(e.target.value)}
          min={today}
          className="input-field"
        />
      </div>

      <button
        onClick={() => setStep(1)}
        className="btn-secondary"
      >
        ← Back
      </button>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Available Time Slots</h3>
        <p className="text-sm text-gray-600">Select a time slot for {selectedDate}</p>
      </div>

      {/* Smart Suggestion */}
      {availableSlots.length > 0 && !selectedSlot && (
        <div className="card p-4 bg-gradient-to-r from-primary-50 to-primary-100 border-primary-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">✨</span>
              <div>
                <p className="font-medium text-primary-900">Next Available Slot: {availableSlots[0]}</p>
                <p className="text-sm text-primary-700">Book this slot quickly or choose another time</p>
              </div>
            </div>
            <button
              onClick={() => handleSlotSelect(availableSlots[0])}
              className="btn-primary"
            >
              Book Now
            </button>
          </div>
          <button
            onClick={() => {}}
            className="mt-3 text-sm text-primary-600 hover:text-primary-800 underline"
          >
            Choose Another Time ↓
          </button>
        </div>
      )}

      {loading ? (
        <div className="card p-8 text-center">
          <Loader2 className="w-8 h-8 text-primary-600 animate-spin mx-auto mb-3" />
          <p className="text-gray-600">Loading available slots...</p>
        </div>
      ) : error ? (
        <div className="card p-6 text-center">
          <XCircle className="w-8 h-8 text-error-500 mx-auto mb-3" />
          <p className="text-error-600 mb-4">{error}</p>
          <button onClick={() => fetchSlots(selectedDate)} className="btn-primary">
            Retry
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Available Slots */}
          {availableSlots.length > 0 && (
            <div className="card p-6">
              <h4 className="font-medium text-success-800 mb-3 flex items-center">
                <CheckCircle className="w-4 h-4 mr-2" />
                🟢 Available Slots
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {availableSlots.map((slot) => (
                  <button
                    key={slot}
                    onClick={() => handleSlotSelect(slot)}
                    className={`slot-chip ${
                      selectedSlot === slot
                        ? 'slot-selected'
                        : 'slot-available'
                    }`}
                  >
                    <Clock className="w-3 h-3 mr-1" />
                    {slot}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Booked Slots */}
          {bookedSlots.length > 0 && (
            <div className="card p-6">
              <h4 className="font-medium text-error-800 mb-3 flex items-center">
                <XCircle className="w-4 h-4 mr-2" />
                🔴 Booked Slots
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {bookedSlots.map((slot) => (
                  <div
                    key={slot}
                    className="slot-chip slot-booked"
                  >
                    <Clock className="w-3 h-3 mr-1" />
                    {slot}
                  </div>
                ))}
              </div>
            </div>
          )}

          {availableSlots.length === 0 && bookedSlots.length === 0 && (
            <div className="card p-6 text-center text-gray-500">
              No slots available for this date. Please try another date.
            </div>
          )}
        </div>
      )}

      {/* Email Participants Section */}
      <div className="card p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <Users className="inline w-4 h-4 mr-2" />
          Add Participants (Emails) - Optional
        </label>
        
        <div className="space-y-3">
          <div className="flex space-x-2">
            <input
              type="email"
              value={emailInput}
              onChange={(e) => setEmailInput(e.target.value)}
              onKeyPress={handleEmailKeyPress}
              placeholder="Enter email address"
              className="flex-1 input-field"
            />
            <button
              onClick={addParticipant}
              disabled={!isValidEmail(emailInput) || participants.includes(emailInput)}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed p-2"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
          
          {participants.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {participants.map((email) => (
                <div
                  key={email}
                  className="inline-flex items-center space-x-1 bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm"
                >
                  <span>{email}</span>
                  <button
                    onClick={() => removeParticipant(email)}
                    className="text-primary-600 hover:text-primary-800"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex space-x-4">
        <button
          onClick={() => setStep(2)}
          className="btn-secondary"
        >
          ← Back
        </button>
        {selectedSlot && (
          <button
            onClick={handleSchedule}
            disabled={loading}
            className="btn-primary disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                Scheduling...
              </>
            ) : (
              'Confirm Schedule →'
            )}
          </button>
        )}
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6 text-center">
      <div className="card p-8">
        <CheckCircle className="w-16 h-16 text-success-500 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Booking Confirmed!</h3>
        <p className="text-gray-600 mb-6">
          Your {type} has been scheduled for {selectedDate} at {selectedSlot}
        </p>
        
        {eventLink && (
          <a
            href={eventLink}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary inline-block"
          >
            View Calendar Event →
          </a>
        )}
      </div>

      <button
        onClick={resetScheduler}
        className="btn-secondary"
      >
        Schedule Another {type.charAt(0).toUpperCase() + type.slice(1)}
      </button>
    </div>
  );

  return (
    <div className="card">
      {/* Progress Indicator */}
      <div className="border-b border-gray-100 p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step >= 1 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              1
            </div>
            <div className={`h-1 w-8 ${
              step >= 2 ? 'bg-primary-600' : 'bg-gray-200'
            }`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step >= 2 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              2
            </div>
            <div className={`h-1 w-8 ${
              step >= 3 ? 'bg-primary-600' : 'bg-gray-200'
            }`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step >= 3 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              3
            </div>
            <div className={`h-1 w-8 ${
              step >= 4 ? 'bg-primary-600' : 'bg-gray-200'
            }`} />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              step >= 4 ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
            }`}>
              4
            </div>
          </div>
        </div>
        <div className="text-xs text-gray-500">
          {step === 1 && 'Select Type'}
          {step === 2 && 'Select Date'}
          {step === 3 && 'Select Time Slot'}
          {step === 4 && 'Confirmation'}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}
        {step === 4 && renderStep4()}
      </div>
    </div>
  );
};

export default SchedulerMode;
