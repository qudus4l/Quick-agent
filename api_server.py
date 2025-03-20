#!/usr/bin/env python3
"""
API Server for Appointment Management System

This script creates a REST API for the appointment management system,
enabling frontend applications to interact with the appointment database
and Twilio call functionality.

Usage:
  python api_server.py
"""

import os
import json
import traceback
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client

# Import from QuickAgent
from QuickAgent import AppointmentDatabase
from appointment_reminder import remind_specific_appointment, parse_appointment_time

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/build')
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for API routes

# Initialize appointment database
appointment_db = AppointmentDatabase()

# Initialize Twilio client - with error handling
try:
    twilio_client = Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )
except Exception as e:
    print(f"Warning: Could not initialize Twilio client: {e}")
    # Create a dummy client that will allow the app to run without Twilio
    class DummyTwilioClient:
        class Calls:
            def list(self, limit=None):
                return []
        
        def __init__(self):
            self.calls = self.Calls()
    
    twilio_client = DummyTwilioClient()

# API Routes
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    """Get all appointments or filter by query parameters."""
    try:
        name = request.args.get('name')
        date = request.args.get('date')
        appointment_id = request.args.get('id')
        
        if appointment_id:
            appointment = appointment_db.get_appointment_by_id(int(appointment_id))
            if appointment:
                # Add calculated time information
                appointment_datetime, days_until = parse_appointment_time(appointment['appointment_time'])
                if appointment_datetime:
                    appointment['datetime'] = appointment_datetime.isoformat()
                    appointment['days_until'] = days_until
                return jsonify(appointment)
            return jsonify({"error": "Appointment not found"}), 404
        
        if name:
            appointments = appointment_db.get_appointments_by_name(name)
        elif date:
            appointments = appointment_db.get_appointments_by_date(date)
        else:
            appointments = appointment_db.get_all_appointments()
        
        # Add calculated time information to each appointment
        for appointment in appointments:
            appointment_datetime, days_until = parse_appointment_time(appointment['appointment_time'])
            if appointment_datetime:
                appointment['datetime'] = appointment_datetime.isoformat()
                appointment['days_until'] = days_until
        
        return jsonify(appointments)
    except Exception as e:
        print(f"Error in get_appointments: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/appointments/<int:appointment_id>/call', methods=['POST'])
def trigger_reminder_call(appointment_id):
    """Trigger a reminder call for a specific appointment."""
    try:
        success = remind_specific_appointment(appointment_id)
        if success:
            return jsonify({"success": True, "message": "Reminder call initiated"})
        else:
            return jsonify({"success": False, "message": "Failed to initiate call"}), 400
    except Exception as e:
        print(f"Error in trigger_reminder_call: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/calls/recent', methods=['GET'])
def get_recent_calls():
    """Get recent calls from Twilio."""
    try:
        # Get recent calls from Twilio
        calls = twilio_client.calls.list(limit=20)
        
        # Format the calls data
        calls_data = []
        for call in calls:
            # Handle if the call object is not iterable or accessible
            try:
                call_data = {
                    'sid': getattr(call, 'sid', 'unknown'),
                    'to': getattr(call, 'to', 'unknown'),
                    'from': getattr(call, 'from_', 'unknown'),
                    'status': getattr(call, 'status', 'unknown'),
                    'direction': getattr(call, 'direction', 'unknown'),
                    'duration': getattr(call, 'duration', 0),
                    'date_created': getattr(call, 'date_created', datetime.now()).isoformat() if hasattr(call, 'date_created') else datetime.now().isoformat()
                }
                calls_data.append(call_data)
            except Exception as e:
                print(f"Error processing call data: {e}")
        
        return jsonify(calls_data)
    except Exception as e:
        print(f"Error in get_recent_calls: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get aggregated data for the dashboard."""
    try:
        # Get all appointments
        appointments = appointment_db.get_all_appointments() or []
        
        # Get recent calls with error handling
        try:
            calls = twilio_client.calls.list(limit=10)
            recent_calls = []
            for call in calls:
                try:
                    call_data = {
                        'sid': getattr(call, 'sid', 'unknown'),
                        'to': getattr(call, 'to', 'unknown'),
                        'from': getattr(call, 'from_', 'unknown'),
                        'status': getattr(call, 'status', 'unknown'),
                        'direction': getattr(call, 'direction', 'unknown'),
                        'duration': getattr(call, 'duration', 0),
                        'date_created': getattr(call, 'date_created', datetime.now()).isoformat() if hasattr(call, 'date_created') else datetime.now().isoformat()
                    }
                    recent_calls.append(call_data)
                except Exception as call_err:
                    print(f"Error processing call data: {call_err}")
        except Exception as e:
            print(f"Error getting call data: {e}")
            recent_calls = []
        
        # Calculate statistics
        today = datetime.now().date()
        upcoming_appointments = []
        past_appointments = []
        
        for appointment in appointments:
            try:
                appointment_datetime, _ = parse_appointment_time(appointment['appointment_time'])
                if appointment_datetime:
                    appointment['datetime'] = appointment_datetime.isoformat()
                    if appointment_datetime.date() >= today:
                        upcoming_appointments.append(appointment)
                    else:
                        past_appointments.append(appointment)
            except Exception as e:
                print(f"Error processing appointment data: {e}")
        
        # Compile dashboard data
        dashboard_data = {
            'total_appointments': len(appointments),
            'upcoming_appointments': len(upcoming_appointments),
            'past_appointments': len(past_appointments),
            'recent_appointments': upcoming_appointments[:5] if upcoming_appointments else [],  # 5 most recent upcoming appointments
            'recent_calls': recent_calls
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        print(f"Error in get_dashboard_data: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/config/phones', methods=['GET'])
def get_phone_numbers():
    """Get Twilio and test client phone numbers from environment variables."""
    try:
        twilio_phone = os.getenv("TWILIO_PHONE_NUMBER", "")
        test_client_phone = os.getenv("TEST_CLIENT_PHONE", "")
        
        return jsonify({
            "twilioPhone": twilio_phone,
            "testClientPhone": test_client_phone
        })
    except Exception as e:
        print(f"Error in get_phone_numbers: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/call/test-client', methods=['POST'])
def call_test_client():
    """Initiate a call from Twilio to the test client phone number."""
    try:
        test_client_phone = os.getenv("TEST_CLIENT_PHONE", "")
        twilio_phone = os.getenv("TWILIO_PHONE_NUMBER", "")
        
        if not test_client_phone or not twilio_phone:
            return jsonify({
                "success": False, 
                "message": "Missing phone numbers in environment variables"
            }), 400
            
        # Create a TwiML response for when the call is answered
        callback_url = f"{os.getenv('PUBLIC_URL', '')}/voice"
        
        try:
            # Initiate the call using Twilio
            call = twilio_client.calls.create(
                to=test_client_phone,
                from_=twilio_phone,
                url=callback_url,
                method="POST"
            )
            
            return jsonify({
                "success": True,
                "message": "Call initiated to test client",
                "call_sid": call.sid
            })
        except Exception as call_err:
            print(f"Error initiating call: {call_err}")
            return jsonify({
                "success": False,
                "message": f"Failed to initiate call: {str(call_err)}"
            }), 500
    except Exception as e:
        print(f"Error in call_test_client: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Serve React frontend in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    try:
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    except Exception as e:
        print(f"Error serving static files: {e}")
        return f"Server error: {str(e)}", 500

# Add routes for favicon and logo
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('frontend/public', 'favicon.ico')

@app.route('/logo192.png')
def logo():
    return send_from_directory('frontend/public', 'logo192.png')

if __name__ == '__main__':
    print("Starting API Server for Appointment Management System...")
    print("Access the dashboard at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True) 