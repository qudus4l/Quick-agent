#!/usr/bin/env python3
"""
Add Appointment Script

This script adds an appointment directly to the database without going through the voice interface.
"""

from QuickAgent import AppointmentDatabase

def add_direct_appointment(name, appointment_time, notes, phone_number=None):
    """Add an appointment directly to the database"""
    db = AppointmentDatabase()
    appointment_id = db.save_appointment(name, appointment_time, notes, phone_number)
    
    print(f"\nAppointment added successfully:")
    print(f"ID: {appointment_id}")
    print(f"Name: {name}")
    print(f"Time: {appointment_time}")
    print(f"Notes: {notes}")
    if phone_number:
        print(f"Phone: {phone_number}")
    print("\nTo check this appointment in the database, run:")
    print(f"python3 QuickAgent.py list id {appointment_id}")

if __name__ == "__main__":
    # Add the appointment from the logs
    name = "Emmanuel Isaiah"
    appointment_time = "Wednesday at 2 p.m."
    notes = "Requesting Doctor John"
    phone_number = "+14376678501"  # From the logs
    
    add_direct_appointment(name, appointment_time, notes, phone_number) 