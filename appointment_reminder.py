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

def should_send_reminder(appointment_datetime):
    """
    Determine if a reminder should be sent for this appointment.
    We'll send reminders in two cases:
    1. It's about 36 hours before the appointment (with a 15-minute window)
    2. It's about 30 minutes before the appointment (with a 5-minute window)
    """
    now = datetime.now()
    
    # Calculate time until appointment
    time_until_appointment = appointment_datetime - now
    hours_until_appointment = time_until_appointment.total_seconds() / 3600
    
    # Define reminder windows
    # 36-hour window: Between 36 hours and 15 minutes before and 35 hours and 45 minutes before
    hours_36_before_start = 36.25  # 36 hours and 15 minutes
    hours_36_before_end = 35.75    # 35 hours and 45 minutes
    
    # 30-minute window: Between 35 minutes and 25 minutes before
    thirty_min_before_start = 0.58  # 35 minutes
    thirty_min_before_end = 0.42    # 25 minutes
    
    # Check if current time falls within either reminder window
    if hours_36_before_end <= hours_until_appointment <= hours_36_before_start:
        return "hours_36_before"  # It's about 36 hours before
    elif thirty_min_before_end <= hours_until_appointment <= thirty_min_before_start:
        return "thirty_min_before"  # It's about 30 minutes before
    else:
        return False  # Not time for a reminder yet

def make_reminder_call(appointment_id, reminder_type):
    """
    Make a phone call to remind a client about their upcoming appointment
    """
    try:
        # Load the appointment details from database
        appointment = get_appointment(appointment_id)
        if not appointment:
            print(f"Could not find appointment with ID {appointment_id}")
            return False
        
        # Extract appointment details
        client_name = appointment.get('client_name', 'valued client')
        appointment_time = format_appointment_time(appointment['appointment_datetime'])
        
        # Get client phone number, or use test number if none is available
        client_phone = appointment.get('phone_number')
        if not client_phone:
            client_phone = os.getenv("TEST_PHONE_NUMBER", "+15551234567")
        
        # Create a context object for the conversational assistant
        context = {
            "is_reminder_call": True,
            "appointment_id": appointment_id,
            "client_name": client_name,
            "appointment_time": appointment_time,
            "reminder_type": reminder_type,
        }
        
        # Encode the context as a URL-safe base64 string
        context_json = json.dumps(context)
        context_encoded = base64.urlsafe_b64encode(context_json.encode()).decode()
        
        # Generate callback URL with context
        callback_url = f"{os.getenv('SERVER_BASE_URL', 'http://localhost:5000')}/voice?reminder_context={context_encoded}"
        
        # Make the call using Twilio
        try:
            from twilio_config import twilio_client
            call = twilio_client.calls.create(
                to=client_phone,
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                url=callback_url,
                method="POST"
            )
            print(f"Call initiated to {client_phone} for appointment {appointment_id}, SID: {call.sid}")
            
            # Update appointment with call status
            update_appointment_reminder_status(appointment_id, reminder_type, "sent")
            return True
        except Exception as e:
            print(f"Error making Twilio call: {e}")
            return False
            
    except Exception as e:
        print(f"Error in make_reminder_call: {e}")
        return False

def check_upcoming_appointments():
    """Check for upcoming appointments and send reminders as needed."""
    print("Checking for upcoming appointments...")
    appointments = appointment_db.get_all_appointments()
    
    reminders_sent = 0
    for appointment in appointments:
        should_remind = should_send_reminder(appointment['appointment_datetime'])
        if should_remind:
            success = make_reminder_call(appointment['id'], should_remind)
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
        success = make_reminder_call(appointment['id'], should_send_reminder(appointment['appointment_datetime']))
        
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