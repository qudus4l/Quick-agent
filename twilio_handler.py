#!/usr/bin/env python3
"""
Twilio Handler for QuickAgent

This script creates a Flask web server that handles Twilio webhooks for voice calls.
It integrates with the QuickAgent system to provide appointment booking and querying
functionality over the phone.

Usage:
  python twilio_handler.py

Requirements:
  - A Twilio account with a phone number
  - Flask and Twilio Python packages
  - ngrok or similar for exposing your local server to the internet
"""

import os
import json
import sqlite3
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
from dotenv import load_dotenv
import threading
import queue
import time
import base64

# Import from QuickAgent
from QuickAgent import AppointmentDatabase, LanguageModelProcessor

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# Initialize language model processor
llm_processor = LanguageModelProcessor()

# Initialize appointment database
appointment_db = AppointmentDatabase()

# Queue for managing conversation state
conversation_queues = {}

@app.route("/voice", methods=["POST"])
def voice_webhook():
    """
    Handle incoming voice calls or outbound reminder calls.
    This function checks if there's a reminder_context parameter, which indicates
    it's an outbound reminder call. Otherwise, it handles regular inbound calls.
    """
    try:
        # Get caller's phone number and call ID
        caller = request.values.get('From', '')
        call_id = request.values.get('CallSid', '')
    
        print(f"Received call from {caller}, call ID: {call_id}")
        
        # Check if this is a reminder call by detecting reminder_context parameter
        reminder_context = request.args.get('reminder_context', None)
        
        # Initialize TwiML response
        response = VoiceResponse()
        
        # Initialize conversation state for this call if it doesn't exist
        if call_id not in conversation_queues:
            conversation_queues[call_id] = queue.Queue()
            print(f"Initialized new conversation for call {call_id}")
        
        # If it's a reminder call, decode the reminder context and use it
        if reminder_context:
            try:
                # Decode base64 context
                print(f"Processing reminder call with context: {reminder_context}")
                decoded_context = base64.urlsafe_b64decode(reminder_context.encode()).decode()
                context_data = json.loads(decoded_context)
                
                # Extract appointment details
                client_name = context_data.get('client_name', 'client')
                appointment_time = context_data.get('appointment_time', 'your upcoming appointment')
                reminder_type = context_data.get('reminder_type', 'general')
                
                print(f"Reminder details: name={client_name}, time={appointment_time}, type={reminder_type}")
                
                # Construct a personalized prompt based on reminder type
                if reminder_type == "hours_36_before":
                    prompt = f"OUTBOUND_REMINDER_CALL: Hi {client_name}, I'm calling to remind you that you have an appointment scheduled in 36 hours at {appointment_time}. Would you like to confirm this appointment, or would you prefer to reschedule or cancel it?"
                elif reminder_type == "thirty_min_before":
                    prompt = f"OUTBOUND_REMINDER_CALL: Hi {client_name}, I'm calling to remind you that you have an appointment coming up in about 30 minutes at {appointment_time}. Are you still able to make it to your appointment today?"
                else:
                    prompt = f"OUTBOUND_REMINDER_CALL: Hi {client_name}, I'm calling about your appointment scheduled for {appointment_time}. I wanted to confirm if you're still planning to attend this appointment?"
                
                # Process the prompt with language model
                print(f"Sending prompt to LLM: {prompt}")
                assistant_response = llm_processor.process(prompt)
                print(f"LLM response: {assistant_response}")
                
                # Gather user input
                gather = Gather(
                    input='speech', 
                    action=f'/handle-input?reminder_context={reminder_context}', 
                    method='POST',
                    timeout=5,
                    speechTimeout="auto"
                )
                gather.say(assistant_response, voice="alice")
                response.append(gather)
                
                # If no input is received, redirect to the input handler
                response.redirect(f'/handle-input?reminder_context={reminder_context}', method='POST')
                
            except Exception as e:
                print(f"Error processing reminder context: {e}")
                import traceback
                traceback.print_exc()
                response.say("Hello, this is your appointment reminder. I'm having trouble accessing your appointment details. Please call us back for assistance.", voice="alice")
        
        else:
            # Regular inbound call
            greeting = "Hello, thanks for calling. How can I help you today?"
            
            # Process greeting with language model
            print(f"Processing inbound call: {greeting}")
            assistant_response = llm_processor.process(greeting)
            print(f"LLM response: {assistant_response}")
            
            # Gather user input
            gather = Gather(
                input='speech', 
                action='/handle-input', 
                method='POST',
                timeout=5,
                speechTimeout="auto"
            )
            gather.say(assistant_response, voice="alice")
            response.append(gather)
            
            # If no input is received, redirect to the input handler
            response.redirect('/handle-input', method='POST')
        
        print(f"Returning TwiML response: {str(response)}")
        return str(response)
        
    except Exception as e:
        print(f"Error in voice_webhook: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a simple response in case of error
        response = VoiceResponse()
        response.say("I'm sorry, we're experiencing technical difficulties. Please try again later.", voice="alice")
        response.hangup()
        return str(response)

@app.route("/handle-input", methods=["POST"])
def handle_input():
    """Process user speech input and generate appropriate responses."""
    try:
        # Get call information
        call_sid = request.values.get("CallSid")
        caller_number = request.values.get("From", "unknown")
        
        print(f"Processing input from call {call_sid}, caller: {caller_number}")
        
        # Get what the user said
        user_input = request.values.get("SpeechResult", "")
        print(f"User input: '{user_input}'")
        
        # Get the reminder context parameter if it exists (for outbound calls)
        reminder_context_encoded = request.args.get("reminder_context")
        reminder_context = None
        
        if reminder_context_encoded:
            try:
                print(f"Processing with reminder context: {reminder_context_encoded}")
                decoded_bytes = base64.urlsafe_b64decode(reminder_context_encoded)
                reminder_context = json.loads(decoded_bytes.decode())
                print(f"Decoded reminder context: {reminder_context}")
            except Exception as e:
                print(f"Error decoding reminder context: {e}")
                import traceback
                traceback.print_exc()
        
        # Initialize TwiML response
        response = VoiceResponse()
        
        if not user_input:
            # If we didn't get any speech, try again
            print("No speech input detected. Prompting for retry.")
            gather = Gather(
                input="speech",
                action=f"/handle-input{('?reminder_context=' + reminder_context_encoded) if reminder_context_encoded else ''}",
                method="POST",
                timeout=5,
                speechTimeout="auto"
            )
            gather.say("I'm sorry, I didn't catch that. Could you please repeat?", voice="alice")
            response.append(gather)
            
            # If nothing is said again, end the call
            response.say("I haven't heard from you. I'll end the call now. Feel free to call back later.", voice="alice")
            response.hangup()
            
            return str(response)
        
        # Process the user input with our language model
        print(f"Sending user input to LLM: {user_input}")
        llm_response = llm_processor.process(user_input)
        print(f"LLM response: {llm_response}")
        
        # Check for special commands in the response
        if "CHECK_APPOINTMENTS:" in llm_response:
            # User is asking about appointments
            name = llm_response.split("CHECK_APPOINTMENTS:")[1].strip()
            appointments = appointment_db.get_appointments_by_name(name)
            
            if appointments:
                # Format appointments for speech
                if len(appointments) == 1:
                    appt = appointments[0]
                    appointment_info = f"I found one appointment for {name}. You're scheduled for {appt['appointment_time']}."
                    if appt.get('notes'):
                        appointment_info += f" Notes: {appt['notes']}."
                else:
                    appointment_info = f"I found {len(appointments)} appointments for {name}. "
                    for i, appt in enumerate(appointments[:3]):  # Limit to first 3 to keep response manageable
                        appointment_info += f"Appointment {i+1}: {appt['appointment_time']}. "
                    if len(appointments) > 3:
                        appointment_info += f"And {len(appointments) - 3} more. "
                
                # Speak the appointment information
                response.say(appointment_info, voice="alice")
            else:
                # No appointments found
                no_appointments_msg = f"I couldn't find any appointments for {name}. Would you like to schedule one now?"
                response.say(no_appointments_msg, voice="alice")
        
        elif "APPOINTMENT_BOOKED:" in llm_response:
            # Extract appointment data
            appointment_info = llm_response.split("APPOINTMENT_BOOKED:")[1].strip()
            name, time, notes = appointment_info.split("|")
            
            # Save appointment to database, including caller's phone number
            appointment_id = appointment_db.save_appointment(
                name=name, 
                appointment_time=time, 
                notes=notes,
                phone_number=caller_number
            )
            
            # Log the appointment with phone number
            print("\nAppointment Details:")
            print(f"Name: {name}")
            print(f"Time: {time}")
            print(f"Notes: {notes}")
            print(f"Phone: {caller_number}")
            print(f"Appointment ID: {appointment_id}")
            
            # Confirm to the user that the appointment was saved
            confirmation = f"Thank you {name.split()[0]}. Your appointment for {time} has been confirmed and saved. Is there anything else I can help you with today?"
            response.say(confirmation, voice="alice")
        
        elif "CANCEL_APPOINTMENT:" in llm_response and reminder_context:
            # Extract the name from the response
            name = llm_response.split("CANCEL_APPOINTMENT:")[1].strip()
            appointment_id = reminder_context.get("appointment_id")
            
            # In a real system, you would implement actual cancellation logic here
            # For now, we'll just acknowledge the cancellation
            
            message = f"I understand you'd like to cancel your appointment, {name}. I've noted your cancellation. Is there anything else I can help you with today?"
            response.say(message, voice="alice")
        
        elif "RESCHEDULE_APPOINTMENT:" in llm_response and reminder_context:
            # Extract rescheduling info
            reschedule_info = llm_response.split("RESCHEDULE_APPOINTMENT:")[1].strip()
            parts = reschedule_info.split("|")
            name = parts[0]
            new_time = parts[1] if len(parts) > 1 else "a new time"
            appointment_id = reminder_context.get("appointment_id")
            
            # In a real system, you would implement actual rescheduling logic here
            # For now, we'll just acknowledge the reschedule request
            
            message = f"Thank you {name}. I've rescheduled your appointment for {new_time}. We look forward to seeing you then. Is there anything else I can help you with?"
            response.say(message, voice="alice")
        
        elif "APPOINTMENT_CONFIRMED:" in llm_response and reminder_context:
            # Extract the name from the response
            name = llm_response.split("APPOINTMENT_CONFIRMED:")[1].strip()
            appointment_id = reminder_context.get("appointment_id")
            appointment_time = reminder_context.get("appointment_time")
            
            # In a real system, you might mark the appointment as confirmed in the database
            
            message = f"Perfect, {name}. Your appointment for {appointment_time} is confirmed. We look forward to seeing you. Is there anything else I can help you with today?"
            response.say(message, voice="alice")
        
        elif "CONVERSATION_ENDED" in llm_response:
            # End the conversation
            farewell = "Thank you for calling. Have a great day!"
            response.say(farewell, voice="alice")
            response.hangup()
            
            # Clean up the conversation state
            if call_sid in conversation_queues:
                del conversation_queues[call_sid]
            
            return str(response)
        
        else:
            # Regular response
            response.say(llm_response, voice="alice")
        
        # Gather next user input
        gather = Gather(
            input="speech",
            action=f"/handle-input{('?reminder_context=' + reminder_context_encoded) if reminder_context_encoded else ''}",
            method="POST",
            timeout=5,
            speechTimeout="auto"
        )
        gather.say("Is there anything else I can help you with?", voice="alice")
        response.append(gather)
        
        # If user doesn't say anything, wrap up the call gracefully
        response.say("Thank you for your time. Feel free to call again if you need any assistance. Goodbye!", voice="alice")
        response.hangup()
        
        return str(response)
        
    except Exception as e:
        print(f"Error in handle_input: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a simple response in case of error
        response = VoiceResponse()
        response.say("I'm sorry, we're experiencing technical difficulties. Please try again later.", voice="alice")
        response.hangup()
        return str(response)

@app.route("/sms", methods=["POST"])
def sms_webhook():
    """Handle incoming SMS messages from Twilio."""
    # Get the sender's phone number and message body
    from_number = request.values.get("From", "unknown")
    body = request.values.get("Body", "").strip()
    
    # Process the message with our language model
    llm_response = llm_processor.process(body)
    
    # Initialize TwiML response
    response = VoiceResponse()
    
    # Check for special commands in the response
    if "CHECK_APPOINTMENTS:" in llm_response:
        # User is asking about appointments
        name = llm_response.split("CHECK_APPOINTMENTS:")[1].strip()
        appointments = appointment_db.get_appointments_by_name(name)
        
        if appointments:
            # Format appointments for text
            if len(appointments) == 1:
                appt = appointments[0]
                appointment_info = f"I found one appointment for {name}. You're scheduled for {appt['appointment_time']}."
                if appt['notes']:
                    appointment_info += f" Notes: {appt['notes']}."
            else:
                appointment_info = f"I found {len(appointments)} appointments for {name}:\n"
                for i, appt in enumerate(appointments):
                    appointment_info += f"{i+1}. {appt['appointment_time']}"
                    if appt['notes']:
                        appointment_info += f" - {appt['notes']}"
                    appointment_info += "\n"
            
            # Send the appointment information
            response.message(appointment_info)
        else:
            # No appointments found
            no_appointments_msg = f"I couldn't find any appointments for {name}. Would you like to schedule one now?"
            response.message(no_appointments_msg)
    
    elif "APPOINTMENT_BOOKED:" in llm_response:
        # Extract appointment data
        appointment_info = llm_response.split("APPOINTMENT_BOOKED:")[1].strip()
        name, time, notes = appointment_info.split("|")
        
        # Save appointment to database, including sender's phone number
        appointment_id = appointment_db.save_appointment(
            name=name,
            appointment_time=time,
            notes=notes,
            phone_number=from_number
        )
        
        # Log the appointment with phone number
        print("\nAppointment Details (SMS):")
        print(f"Name: {name}")
        print(f"Time: {time}")
        print(f"Notes: {notes}")
        print(f"Phone: {from_number}")
        print(f"Appointment ID: {appointment_id}")
        
        # Confirm to the user that the appointment was saved
        confirmation = f"Thank you {name.split()[0]}. Your appointment for {time} has been confirmed and saved. Is there anything else I can help you with today?"
        response.message(confirmation)
    
    elif "CONVERSATION_ENDED" in llm_response:
        # End the conversation
        farewell = "Thank you for your message. Have a great day!"
        response.message(farewell)
    
    else:
        # Regular response
        response.message(llm_response)
    
    return Response(str(response), mimetype="text/xml")

@app.route("/appointment-action", methods=["POST"])
def appointment_action():
    """Handle responses to appointment reminder calls."""
    # Get information from the request
    call_sid = request.values.get("CallSid")
    appointment_id = request.values.get("id")
    digits_pressed = request.values.get("Digits")
    
    # Initialize TwiML response
    response = VoiceResponse()
    
    # If this is the initial call (no digits yet)
    if not digits_pressed:
        try:
            # Get appointment details
            appointment = appointment_db.get_appointment_by_id(int(appointment_id))
            if not appointment:
                response.say("I'm sorry, but I couldn't find information about your appointment.", voice="alice")
                response.hangup()
                return Response(str(response), mimetype="text/xml")
            
            # Create the initial message
            name = appointment['name']
            time = appointment['appointment_time']
            
            greeting = f"Hello {name.split()[0]}! This is a reminder about your appointment scheduled for {time}."
            if appointment['notes']:
                greeting += f" The notes for your appointment indicate: {appointment['notes']}."
            
            greeting += " Press 1 to confirm this appointment, press 2 if you need to reschedule, or press 3 to cancel."
            
            # Gather input from the user
            gather = Gather(
                num_digits=1,
                action=f"/appointment-action?id={appointment_id}",
                method="POST"
            )
            gather.say(greeting, voice="alice")
            response.append(gather)
            
            # If no input is received, try again
            response.redirect(f"/appointment-action?id={appointment_id}")
            
        except Exception as e:
            print(f"Error in appointment-action: {e}")
            response.say("I'm sorry, there was an error processing your appointment. Please call our office directly.", voice="alice")
            response.hangup()
    
    # Process user input
    else:
        try:
            appointment = appointment_db.get_appointment_by_id(int(appointment_id))
            
            # Handle based on user input
            if digits_pressed == "1":  # Confirm
                response.say("Thank you for confirming your appointment. We look forward to seeing you!", voice="alice")
                response.hangup()
                
            elif digits_pressed == "2":  # Reschedule
                # For a simple demo, we'll just gather input for a new day
                response.say(
                    "I understand you'd like to reschedule. In a real system, I would transfer you to a booking agent "
                    "or allow you to select a new time. For this demo, please call our office directly to reschedule. "
                    "Thank you for your understanding.", 
                    voice="alice"
                )
                response.hangup()
                
            elif digits_pressed == "3":  # Cancel
                # Handle cancellation
                # In a real system, you would update the database here
                response.say(
                    "I understand you'd like to cancel your appointment. In a real system, I would cancel it now. "
                    "For this demo, please call our office directly to cancel. Thank you for your understanding.",
                    voice="alice"
                )
                response.hangup()
                
            else:
                # Invalid input
                gather = Gather(
                    num_digits=1,
                    action=f"/appointment-action?id={appointment_id}",
                    method="POST"
                )
                gather.say(
                    "I'm sorry, I didn't understand your selection. Press 1 to confirm your appointment, "
                    "press 2 to reschedule, or press 3 to cancel.",
                    voice="alice"
                )
                response.append(gather)
        
        except Exception as e:
            print(f"Error processing appointment action: {e}")
            response.say("I'm sorry, there was an error processing your request. Please call our office directly.", voice="alice")
            response.hangup()
    
    return Response(str(response), mimetype="text/xml")

@app.route("/make-test-call", methods=["GET"])
def make_test_call():
    """A simple endpoint to trigger a test reminder call."""
    # This is just for testing - in production you'd use proper authentication
    appointment_id = request.args.get("id")
    if not appointment_id:
        return "Error: No appointment ID provided. Use ?id=X in the URL."
    
    try:
        from appointment_reminder import remind_specific_appointment
        result = remind_specific_appointment(appointment_id)
        if result:
            return "Test call initiated successfully!"
        else:
            return "Failed to initiate test call. Check the server logs for details."
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Check if Twilio credentials are set
    if not os.getenv("TWILIO_ACCOUNT_SID") or not os.getenv("TWILIO_AUTH_TOKEN"):
        print("Error: Twilio credentials not found in .env file.")
        print("Please add TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN to your .env file.")
        exit(1)
    
    # Run the Flask app
    print("Starting Twilio webhook handler...")
    print("Make sure to expose this server to the internet using ngrok or similar.")
    print("Then configure your Twilio phone number to use the following webhooks:")
    print("  Voice: http://your-domain.com/voice")
    print("  SMS: http://your-domain.com/sms")
    app.run(debug=True, port=5000) 