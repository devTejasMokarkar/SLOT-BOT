// Contextual status messages for different processing steps
export const statusMessages = {
  // Initial processing
  understanding: "🧠 Understanding your request...",
  
  // Availability checking
  checking_availability: "📅 Checking availability...",
  
  // Slot finding
  finding_slots: "🔍 Finding available slots...",
  
  // Scheduling
  scheduling: "⚡ Scheduling your meeting...",
  
  // Adding participants
  adding_participants: "📧 Adding participants...",
  
  // Final success
  completing: "✅ Meeting scheduled successfully",
  
  // Default fallback
  default: "SlotBot is typing..."
};

// Get status message based on message content and context
export const getStatusMessage = (userMessage, currentStep = null) => {
  if (currentStep) {
    return statusMessages[currentStep] || statusMessages.default;
  }
  
  // Infer status from message content
  const message = userMessage.toLowerCase();
  
  if (message.includes('schedule') || message.includes('meeting') || message.includes('appointment')) {
    return statusMessages.understanding;
  }
  
  if (message.includes('available') || message.includes('free') || message.includes('when')) {
    return statusMessages.checking_availability;
  }
  
  if (message.includes('time') || message.includes('slot')) {
    return statusMessages.finding_slots;
  }
  
  if (message.includes('confirm') || message.includes('book') || message.includes('create')) {
    return statusMessages.scheduling;
  }
  
  return statusMessages.default;
};
