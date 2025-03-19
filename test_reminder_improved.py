#!/usr/bin/env python3
"""
Improved Local Testing Script for Appointment Reminders

This script more accurately simulates the conversational assistant for appointment reminders.
It clearly separates the assistant's role from the client's role in the conversation.
"""

import sys
import json
import base64
from QuickAgent import AppointmentDatabase, LanguageModelProcessor

# Initialize appointment database
appointment_db = AppointmentDatabase()

class ReminderTester:
    def __init__(self):
        # Create a separate instance for the assistant's LLM
        self.assistant_llm = LanguageModelProcessor()
        # We're not simulating the client with LLM, but you could if needed
        
    def test_reminder(self, appointment_id, reminder_type="thirty_min_before"):
        """Simulate a conversation with the reminder assistant for a specific appointment."""
        print(f"\n========== TESTING REMINDER FOR APPOINTMENT ID: {appointment_id} ==========\n")
        
        # Get the appointment from the database
        appointment = appointment_db.get_appointment_by_id(int(appointment_id))
        if not appointment:
            print(f"Error: Appointment with ID {appointment_id} not found.")
            return
        
        print(f"Found appointment: {appointment['name']} at {appointment['appointment_time']}")
        
        # Create a reminder context
        reminder_context = {
            "appointment_id": appointment['id'],
            "appointment_time": appointment['appointment_time'],
            "client_name": appointment['name'],
            "reminder_type": reminder_type,
            "is_reminder_call": True
        }
        
        # Print the reminder context for reference
        print("\nReminder Context:")
        for key, value in reminder_context.items():
            print(f"  {key}: {value}")
        
        # Construct the initial prompt for the LLM - this is what would normally be in twilio_handler.py
        if reminder_context["reminder_type"] == "day_before":
            initial_prompt = f"OUTBOUND_REMINDER_CALL: Hi {reminder_context['client_name']}, I'm calling to remind you that you have an appointment scheduled for tomorrow at {reminder_context['appointment_time']}. Would you like to confirm this appointment, or would you prefer to reschedule or cancel it?"
        elif reminder_context["reminder_type"] == "thirty_min_before":
            initial_prompt = f"OUTBOUND_REMINDER_CALL: Hi {reminder_context['client_name']}, I'm calling to remind you that you have an appointment coming up in about 30 minutes at {reminder_context['appointment_time']}. Are you still able to make it to your appointment today?"
        else:
            initial_prompt = f"OUTBOUND_REMINDER_CALL: Hi {reminder_context['client_name']}, I'm calling about your appointment scheduled for {reminder_context['appointment_time']}. I wanted to confirm if you're still planning to attend this appointment?"
        
        # Generate the assistant's greeting
        print("\nSimulating Assistant's Initial Greeting...")
        greeting = self.assistant_llm.process(initial_prompt)
        
        # Analyze the greeting for special commands
        if self._check_for_commands(greeting):
            # If there's a special command, this was likely a misinterpretation
            # We'll generate a more appropriate greeting
            print("\nDetected command in greeting, regenerating appropriate greeting...")
            greeting = f"Hi {reminder_context['client_name']}, this is your appointment reminder. You have an appointment scheduled for {reminder_context['appointment_time']}. Would you like to confirm, reschedule, or cancel?"
        
        # Begin conversation loop
        print("\n=== Beginning Conversation ===")
        print(f"Assistant: {greeting}")
        
        conversation_active = True
        while conversation_active:
            # Get user input (simulating the client)
            user_input = input("\nYou (Client): ")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nEnding test conversation.")
                break
            
            # Process with the assistant's language model
            print("\nAssistant is processing...")
            response = self.assistant_llm.process(user_input)
            
            # Check for special commands in the response
            self._check_for_commands(response)
            
            # Display the response
            print(f"Assistant: {response}")
            
            # Check if conversation should end
            if "CONVERSATION_ENDED" in response:
                print("\nConversation ended naturally.")
                conversation_active = False
        
        print("\n========== TEST COMPLETED ==========")
    
    def _check_for_commands(self, response):
        """Check for and handle special commands in the LLM response."""
        has_command = False
        
        if "CANCEL_APPOINTMENT:" in response:
            name = response.split("CANCEL_APPOINTMENT:")[1].strip()
            print(f"\n[ACTION DETECTED] Cancel appointment for {name}")
            print(f"[SYSTEM] In a real call, the appointment would be canceled in the database.")
            has_command = True
            
        elif "RESCHEDULE_APPOINTMENT:" in response:
            reschedule_info = response.split("RESCHEDULE_APPOINTMENT:")[1].strip()
            parts = reschedule_info.split("|")
            name = parts[0]
            new_time = parts[1] if len(parts) > 1 else "a new time"
            print(f"\n[ACTION DETECTED] Reschedule appointment for {name} to {new_time}")
            print(f"[SYSTEM] In a real call, the appointment would be rescheduled in the database.")
            has_command = True
            
        elif "APPOINTMENT_CONFIRMED:" in response:
            name = response.split("APPOINTMENT_CONFIRMED:")[1].strip()
            print(f"\n[ACTION DETECTED] Appointment confirmed for {name}")
            print(f"[SYSTEM] In a real call, the appointment would be marked as confirmed in the database.")
            has_command = True
            
        elif "CONVERSATION_ENDED" in response:
            print("\n[ACTION DETECTED] Conversation ended naturally.")
            has_command = True
            
        return has_command

def print_help():
    print("\nUsage:")
    print("  python3 test_reminder_improved.py [appointment_id] [reminder_type]")
    print("\nReminder Types:")
    print("  day_before        - Test a reminder sent one day before the appointment")
    print("  thirty_min_before - Test a reminder sent 30 minutes before the appointment")
    print("  general           - Test a general reminder")
    print("\nExample:")
    print("  python3 test_reminder_improved.py 1 day_before")
    print("  python3 test_reminder_improved.py 2 thirty_min_before")
    print("  python3 test_reminder_improved.py 3 general")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_help()
        sys.exit(0)
        
    appointment_id = sys.argv[1]
    reminder_type = sys.argv[2] if len(sys.argv) > 2 else "thirty_min_before"
    
    # Validate reminder type
    valid_types = ["day_before", "thirty_min_before", "general"]
    if reminder_type not in valid_types:
        print(f"Error: Invalid reminder type '{reminder_type}'")
        print(f"Valid types are: {', '.join(valid_types)}")
        sys.exit(1)
        
    tester = ReminderTester()
    tester.test_reminder(appointment_id, reminder_type) 