#!/usr/bin/env python3
"""
Appointment Reminder System

This script makes outgoing calls to remind users of their upcoming appointments.
It uses Twilio for making calls and interacts with the appointment database.

Usage:
  python appointment_reminder.py check         # Check for upcoming appointments and send reminders
  python appointment_reminder.py remind ID     # Send a reminder for a specific appointment ID
  python appointment_reminder.py schedule      # Run as a daemon to schedule reminders automatically
"""

import os
import sys
import json
import time
import sqlite3
import datetime
import schedule
import argparse
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import base64

# Import from QuickAgent
from QuickAgent import AppointmentDatabase, LanguageModelProcessor

# Load environment variables
load_dotenv()

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# Initialize language model processor
llm_processor = LanguageModelProcessor()

# Initialize appointment database
appointment_db = AppointmentDatabase()

def parse_appointment_time(appointment_time):
    """
    Parse appointment time string into a datetime object.
    Handles formats like "Tuesday at 10:00", "Wednesday at 16:00", etc.
    
    Returns a tuple of (parsed_datetime, days_until)
    """
    today = datetime.datetime.now()
    weekday_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    # Extract the day and time
    try:
        day_str, time_str = appointment_time.lower().split(' at ')
        day = day_str.strip()
        time_parts = time_str.strip().split(':')
        
        # Handle 24-hour format (e.g., "16:00") or 12-hour format (e.g., "4 PM")
        if len(time_parts) == 2 and time_parts[1].isdigit():
            hour = int(time_parts[0])
            minute = int(time_parts[1])
        else:
            # Handle formats like "4 PM"
            if "pm" in time_str.lower() and int(time_parts[0]) < 12:
                hour = int(time_parts[0]) + 12
            else:
                hour = int(time_parts[0])
            minute = 0
        
        # Get the target weekday
        target_weekday = weekday_map.get(day.lower())
        if target_weekday is None:
            # If it's not a recognized weekday, return None
            return None, None
        
        # Calculate days until appointment
        days_until = (target_weekday - today.weekday()) % 7
        
        # If it's the same day, check if the time has passed
        if days_until == 0 and (hour < today.hour or (hour == today.hour and minute <= today.minute)):
            days_until = 7  # Schedule for next week
        
        # Create the appointment datetime
        appointment_date = today + datetime.timedelta(days=days_until)
        appointment_datetime = appointment_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return appointment_datetime, days_until
    
    except Exception as e:
        print(f"Error parsing appointment time: {e}")
        return None, None

def should_send_reminder(appointment):
    """
    Determine if a reminder should be sent for this appointment.
    
    Reminders will be sent:
    1. One day before the appointment
    2. 30 minutes before the appointment (changed from 1 hour)
    """
    appointment_time = appointment['appointment_time']
    appointment_datetime, days_until = parse_appointment_time(appointment_time)
    
    if appointment_datetime is None:
        return False, None
    
    now = datetime.datetime.now()
    
    # One day before
    one_day_before = appointment_datetime - datetime.timedelta(days=1)
    one_day_window = (
        one_day_before - datetime.timedelta(minutes=15),
        one_day_before + datetime.timedelta(minutes=15)
    )
    
    # 30 minutes before (changed from 1 hour)
    thirty_min_before = appointment_datetime - datetime.timedelta(minutes=30)
    thirty_min_window = (
        thirty_min_before - datetime.timedelta(minutes=5),
        thirty_min_before + datetime.timedelta(minutes=5)
    )
    
    # Check if current time falls within reminder windows
    if one_day_window[0] <= now <= one_day_window[1]:
        return True, "day_before"
    elif thirty_min_window[0] <= now <= thirty_min_window[1]:
        return True, "thirty_min_before"
    
    return False, None

def make_reminder_call(appointment, reminder_type="general"):
    """
    Make an outgoing call to remind the user of their appointment.
    The call will connect to the conversational assistant for natural language interaction.
    
    Parameters:
    - appointment: The appointment record from the database
    - reminder_type: 'day_before', 'thirty_min_before', or 'general'
    """
    # Get phone number for this client - use stored number if available
    client_phone = appointment.get('phone_number')
    
    # Fall back to test phone if no stored number
    if not client_phone:
        client_phone = os.getenv("TEST_CLIENT_PHONE")
        print(f"No stored phone number found, using test number: {client_phone}")
    
    if not client_phone:
        print("Error: No phone number available for this appointment")
        return False
    
    # Create a context parameter that informs the assistant this is a reminder call
    reminder_context = {
        "appointment_id": appointment['id'],
        "appointment_time": appointment['appointment_time'],
        "client_name": appointment['name'],
        "reminder_type": reminder_type,
        "is_reminder_call": True  # Flag to identify this as a reminder call
    }
    
    # Encode context as URL-safe base64 string
    context_json = json.dumps(reminder_context)
    encoded_context = base64.urlsafe_b64encode(context_json.encode()).decode()
    
    # Create a callback URL for the assistant
    callback_url = f"{os.getenv('PUBLIC_URL', 'http://example.com')}/voice?reminder_context={encoded_context}"
    
    try:
        # Make the call
        call = twilio_client.calls.create(
            to=client_phone,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            url=callback_url,
            method="POST"
        )
        
        print(f"Reminder call initiated for {appointment['name']} to {client_phone} - Call SID: {call.sid}")
        return True
        
    except Exception as e:
        print(f"Error making reminder call: {e}")
        return False

def check_upcoming_appointments():
    """Check for upcoming appointments and send reminders as needed."""
    print("Checking for upcoming appointments...")
    appointments = appointment_db.get_all_appointments()
    
    reminders_sent = 0
    for appointment in appointments:
        should_remind, reminder_type = should_send_reminder(appointment)
        if should_remind:
            success = make_reminder_call(appointment, reminder_type)
            if success:
                reminders_sent += 1
    
    print(f"Reminder check complete. Sent {reminders_sent} reminder(s).")
    return reminders_sent

def remind_specific_appointment(appointment_id):
    """
    Trigger a reminder call for a specific appointment by ID.
    
    This function is used by the API to manually trigger reminder calls.
    
    Parameters:
    - appointment_id: The ID of the appointment to send a reminder for
    
    Returns:
    - Boolean indicating success or failure
    """
    print(f"Manually triggering reminder for appointment ID: {appointment_id}")
    
    try:
        # Get the appointment from the database
        db = AppointmentDatabase()
        appointment = db.get_appointment_by_id(appointment_id)
        
        if not appointment:
            print(f"Appointment with ID {appointment_id} not found")
            return False
        
        # Make the reminder call
        success = make_reminder_call(appointment, reminder_type="general")
        
        return success
    except Exception as e:
        print(f"Error triggering reminder: {e}")
        return False

def run_scheduler():
    """Run as a daemon to schedule reminders automatically."""
    print("Starting appointment reminder scheduler...")
    print("The scheduler will check for appointments requiring reminders every 15 minutes.")
    print("Press Ctrl+C to stop.")
    
    # Schedule checks every 15 minutes
    schedule.every(15).minutes.do(check_upcoming_appointments)
    
    # Also run once at startup
    check_upcoming_appointments()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Sleep for 1 minute between checks
    except KeyboardInterrupt:
        print("\nStopping scheduler...")

def main():
    parser = argparse.ArgumentParser(description="Appointment Reminder System")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Check command
    check_parser = subparsers.add_parser("check", help="Check for upcoming appointments and send reminders")
    
    # Remind command
    remind_parser = subparsers.add_parser("remind", help="Send a reminder for a specific appointment")
    remind_parser.add_argument("id", help="Appointment ID to remind")
    
    # Schedule command
    schedule_parser = subparsers.add_parser("schedule", help="Run as a daemon to schedule reminders automatically")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check for Twilio credentials
    if not os.getenv("TWILIO_ACCOUNT_SID") or not os.getenv("TWILIO_AUTH_TOKEN"):
        print("Error: Twilio credentials not found in .env file.")
        print("Please add TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN to your .env file.")
        sys.exit(1)
    
    # Execute command
    if args.command == "check":
        check_upcoming_appointments()
    elif args.command == "remind":
        remind_specific_appointment(args.id)
    elif args.command == "schedule":
        run_scheduler()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 