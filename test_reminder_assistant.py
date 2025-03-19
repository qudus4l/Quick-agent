#!/usr/bin/env python3
"""
Local Testing Script for Conversational Appointment Reminder

This script simulates a conversation with the reminder assistant locally, 
without actually making Twilio calls. It's useful for testing the language
model responses and the conversational flow.
"""

import json
import base64
from QuickAgent import AppointmentDatabase, LanguageModelProcessor

# Initialize the language model processor
llm_processor = LanguageModelProcessor()

# Initialize appointment database
appointment_db = AppointmentDatabase()

def test_reminder_conversation():
    """Simulate a conversation with the reminder assistant locally."""
    print("\n========== LOCAL APPOINTMENT REMINDER CONVERSATION TEST ==========\n")
    
    # Step 1: Get an appointment from the database
    appointments = appointment_db.get_all_appointments()
    if not appointments:
        print("No appointments found in the database. Please add an appointment first.")
        return
    
    # Take the first appointment for testing
    appointment = appointments[0]
    print(f"Found appointment: {appointment['name']} at {appointment['appointment_time']}")
    
    # Step 2: Create a reminder context (similar to what would be created in make_reminder_call)
    reminder_context = {
        "appointment_id": appointment['id'],
        "appointment_time": appointment['appointment_time'],
        "client_name": appointment['name'],
        "reminder_type": "thirty_min_before",  # Options: "day_before", "thirty_min_before", "general"
        "is_reminder_call": True
    }
    
    # Print the reminder context for reference
    print("\nReminder Context:")
    for key, value in reminder_context.items():
        print(f"  {key}: {value}")
    
    # Step 3: Construct the initial prompt for the LLM (similar to voice_webhook)
    if reminder_context["reminder_type"] == "day_before":
        initial_prompt = f"OUTBOUND_REMINDER_CALL: Hi {reminder_context['client_name']}, I'm calling to remind you that you have an appointment scheduled for tomorrow at {reminder_context['appointment_time']}. Would you like to confirm this appointment, or would you prefer to reschedule or cancel it?"
    elif reminder_context["reminder_type"] == "thirty_min_before":
        initial_prompt = f"OUTBOUND_REMINDER_CALL: Hi {reminder_context['client_name']}, I'm calling to remind you that you have an appointment coming up in about 30 minutes at {reminder_context['appointment_time']}. Are you still able to make it to your appointment today?"
    else:
        initial_prompt = f"OUTBOUND_REMINDER_CALL: Hi {reminder_context['client_name']}, I'm calling about your appointment scheduled for {reminder_context['appointment_time']}. I wanted to confirm if you're still planning to attend this appointment?"
    
    # Step 4: Process with the language model to get the greeting
    print("\nAssistant's Initial Greeting:")
    greeting = llm_processor.process(initial_prompt)
    print(f"  {greeting}")
    
    # Step 5: Begin conversation loop
    print("\n=== Beginning Conversation ===")
    print(f"Assistant: {greeting}")
    
    conversation_active = True
    while conversation_active:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nEnding test conversation.")
            break
        
        # Process with language model
        print("\nProcessing...")
        response = llm_processor.process(user_input)
        
        # Check for special commands
        if "CANCEL_APPOINTMENT:" in response:
            name = response.split("CANCEL_APPOINTMENT:")[1].strip()
            print(f"\nAction detected: Cancel appointment for {name}")
            print(f"In a real call, this would cancel the appointment in the database.")
            
        elif "RESCHEDULE_APPOINTMENT:" in response:
            reschedule_info = response.split("RESCHEDULE_APPOINTMENT:")[1].strip()
            parts = reschedule_info.split("|")
            name = parts[0]
            new_time = parts[1] if len(parts) > 1 else "a new time"
            print(f"\nAction detected: Reschedule appointment for {name} to {new_time}")
            print(f"In a real call, this would reschedule the appointment in the database.")
            
        elif "APPOINTMENT_CONFIRMED:" in response:
            name = response.split("APPOINTMENT_CONFIRMED:")[1].strip()
            print(f"\nAction detected: Appointment confirmed for {name}")
            print(f"In a real call, this would mark the appointment as confirmed in the database.")
            
        elif "CONVERSATION_ENDED" in response:
            print("\nConversation ended naturally.")
            conversation_active = False
        
        # Display the response
        print(f"Assistant: {response}")
        
    print("\n========== TEST COMPLETED ==========")

if __name__ == "__main__":
    test_reminder_conversation() 