import React, { useState } from 'react';
import { Calendar, Clock, CheckCircle, XCircle, Loader2, Users, CalendarDays } from 'lucide-react';
import { apiService } from '../services/api';

const SchedulerMode = () => {
  const [step, setStep] = useState(1); // 1: Type selection, 2: Action selection, 3: Date selection, 4: Slot selection, 5: Confirmation
  const [type, setType] = useState(''); // 'appointment' | 'meeting'
  const [action, setAction] = useState(''); // 'view_slots' | 'schedule'
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedSlot, setSelectedSlot] = useState('');
  const [availableSlots, setAvailableSlots] = useState([]);
  const [bookedSlots, setBookedSlots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [eventLink, setEventLink] = useState('');

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
    }
  };

  const handleSlotSelect = (slot) => {
    if (bookedSlots.includes(slot)) {
      return; // Don't allow selection of booked slots
    }
    setSelectedSlot(slot);
  };

  const handleSchedule = async () => {
    if (!selectedDate || !selectedSlot) return;

    setLoading(true);
    setError('');

    try {
      // Convert to ISO format
      apiService.slotToIso(selectedDate, selectedSlot);
      
      // Call the UI chat endpoint for scheduling
      const response = await apiService.uiChat({
        message: '',
        session_id: `scheduler_${Date.now()}`,
        selected_action: 'schedule',
        selected_date: selectedDate,
        selected_slot: selectedSlot
      });

      if (response.event_link) {
        setEventLink(response.event_link);
        setStep(5); // Success step
      } else {
        setError('Failed to schedule meeting. Please try again.');
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
    setAction('');
    setSelectedDate('');
    setSelectedSlot('');
    setAvailableSlots([]);
    setBookedSlots([]);
    setError('');
    setEventLink('');
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">What would you like to schedule?</h3>
        <p className="text-sm text-gray-600">Choose the type of booking you need</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => {
            setType('appointment');
            setStep(2);
          }}
          className="card p-6 hover:shadow-lg transition-shadow duration-200 text-left group"
        >
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 p-3 rounded-lg group-hover:bg-blue-200 transition-colors">
              <CalendarDays className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">Appointment</h4>
              <p className="text-sm text-gray-600">One-on-one session</p>
            </div>
          </div>
        </button>

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
              <p className="text-sm text-gray-600">Group discussion</p>
            </div>
          </div>
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">What would you like to do?</h3>
        <p className="text-sm text-gray-600">Choose an action for your {type}</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => {
            setAction('view_slots');
            setStep(3);
          }}
          className="card p-6 hover:shadow-lg transition-shadow duration-200 text-left group"
        >
          <div className="flex items-center space-x-4">
            <div className="bg-purple-100 p-3 rounded-lg group-hover:bg-purple-200 transition-colors">
              <Clock className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">View Available Slots</h4>
              <p className="text-sm text-gray-600">Check what times are free</p>
            </div>
          </div>
        </button>

        <button
          onClick={() => {
            setAction('schedule');
            setStep(3);
          }}
          className="card p-6 hover:shadow-lg transition-shadow duration-200 text-left group"
        >
          <div className="flex items-center space-x-4">
            <div className="bg-primary-100 p-3 rounded-lg group-hover:bg-primary-200 transition-colors">
              <Calendar className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">Schedule {type.charAt(0).toUpperCase() + type.slice(1)}</h4>
              <p className="text-sm text-gray-600">Book a time slot</p>
            </div>
          </div>
        </button>
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
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Select Date</h3>
        <p className="text-sm text-gray-600">Choose your preferred date</p>
      </div>

      <div className="card p-6">
        <label htmlFor="date-picker" className="block text-sm font-medium text-gray-700 mb-2">
          <Calendar className="inline w-4 h-4 mr-2" />
          Select Date
        </label>
        <input
          id="date-picker"
          type="date"
          value={selectedDate}
          onChange={(e) => handleDateChange(e.target.value)}
          min={today}
          className="input-field"
        />
      </div>

      <div className="flex space-x-4">
        <button
          onClick={() => setStep(2)}
          className="btn-secondary"
        >
          ← Back
        </button>
        {selectedDate && (
          <button
            onClick={() => setStep(4)}
            className="btn-primary"
          >
            Continue →
          </button>
        )}
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Available Time Slots</h3>
        <p className="text-sm text-gray-600">Select a time slot for {selectedDate}</p>
      </div>

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
              No slots available for this date
            </div>
          )}
        </div>
      )}

      <div className="flex space-x-4">
        <button
          onClick={() => setStep(3)}
          className="btn-secondary"
        >
          ← Back
        </button>
        {selectedSlot && action === 'schedule' && (
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

  const renderStep5 = () => (
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
          {step === 2 && 'Select Action'}
          {step === 3 && 'Select Date'}
          {step === 4 && 'Select Time Slot'}
          {step === 5 && 'Confirmation'}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}
        {step === 3 && renderStep3()}
        {step === 4 && renderStep4()}
        {step === 5 && renderStep5()}
      </div>
    </div>
  );
};

export default SchedulerMode;
