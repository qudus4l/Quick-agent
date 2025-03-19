#!/usr/bin/env python3
"""
Appointment Manager - A command-line utility to manage appointments stored by QuickAgent.

Usage:
  python appointment_manager.py list                  # List all appointments
  python appointment_manager.py list name "John Doe"  # Search by name
  python appointment_manager.py list date "Tuesday"   # Search by date
  python appointment_manager.py list id 1             # Get appointment by ID
  python appointment_manager.py export [filename]     # Export appointments to JSON
  python appointment_manager.py import filename       # Import appointments from JSON
  python appointment_manager.py delete id             # Delete an appointment by ID
"""

import sys
import json
import sqlite3
import os
from datetime import datetime

class AppointmentManager:
    def __init__(self, db_path="appointments.db"):
        self.db_path = db_path
        self._check_db_exists()
    
    def _check_db_exists(self):
        """Check if the database file exists."""
        if not os.path.exists(self.db_path):
            print(f"Error: Database file '{self.db_path}' not found.")
            print("You need to run QuickAgent and book at least one appointment first.")
            sys.exit(1)
    
    def list_appointments(self, filter_type=None, filter_value=None):
        """List appointments with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM appointments"
        params = []
        
        if filter_type == "id":
            query += " WHERE id = ?"
            params.append(int(filter_value))
        elif filter_type == "name":
            query += " WHERE name LIKE ?"
            params.append(f"%{filter_value}%")
        elif filter_type == "date":
            query += " WHERE appointment_time LIKE ?"
            params.append(f"%{filter_value}%")
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        if not appointments:
            print("No appointments found.")
            return []
        
        print(f"\nFound {len(appointments)} appointment(s):")
        for appt in appointments:
            print(f"ID: {appt['id']}")
            print(f"Name: {appt['name']}")
            print(f"Time: {appt['appointment_time']}")
            print(f"Notes: {appt['notes']}")
            print(f"Created: {appt['created_at']}")
            print("-" * 40)
        
        return appointments
    
    def export_appointments(self, filename=None):
        """Export all appointments to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"appointments_export_{timestamp}.json"
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM appointments ORDER BY created_at DESC")
        appointments = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        with open(filename, 'w') as f:
            json.dump(appointments, f, indent=2)
        
        print(f"Exported {len(appointments)} appointments to {filename}")
    
    def import_appointments(self, filename):
        """Import appointments from a JSON file."""
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found.")
            return
        
        try:
            with open(filename, 'r') as f:
                appointments = json.load(f)
            
            if not isinstance(appointments, list):
                print("Error: Invalid JSON format. Expected a list of appointments.")
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            for appt in appointments:
                # Check if appointment has required fields
                if not all(key in appt for key in ['name', 'appointment_time']):
                    print(f"Skipping invalid appointment: {appt}")
                    continue
                
                # Use get() to handle optional fields
                notes = appt.get('notes', '')
                
                cursor.execute(
                    "INSERT INTO appointments (name, appointment_time, notes) VALUES (?, ?, ?)",
                    (appt['name'], appt['appointment_time'], notes)
                )
                imported_count += 1
            
            conn.commit()
            conn.close()
            
            print(f"Successfully imported {imported_count} appointments.")
            
        except json.JSONDecodeError:
            print(f"Error: '{filename}' is not a valid JSON file.")
        except Exception as e:
            print(f"Error importing appointments: {e}")
    
    def delete_appointment(self, appointment_id):
        """Delete an appointment by ID."""
        try:
            appointment_id = int(appointment_id)
        except ValueError:
            print("Error: Appointment ID must be a number.")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First check if the appointment exists
        cursor.execute("SELECT id FROM appointments WHERE id = ?", (appointment_id,))
        if not cursor.fetchone():
            print(f"Error: No appointment found with ID {appointment_id}")
            conn.close()
            return
        
        # Delete the appointment
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
        
        print(f"Successfully deleted appointment with ID {appointment_id}")

def print_usage():
    """Print usage instructions."""
    print(__doc__)

def main():
    """Main entry point for the appointment manager."""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    manager = AppointmentManager()
    command = sys.argv[1].lower()
    
    if command == "list":
        if len(sys.argv) > 3:
            filter_type = sys.argv[2].lower()
            filter_value = sys.argv[3]
            manager.list_appointments(filter_type, filter_value)
        else:
            manager.list_appointments()
    
    elif command == "export":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        manager.export_appointments(filename)
    
    elif command == "import":
        if len(sys.argv) < 3:
            print("Error: Missing filename for import.")
            print_usage()
        else:
            manager.import_appointments(sys.argv[2])
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: Missing appointment ID for deletion.")
            print_usage()
        else:
            manager.delete_appointment(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")
        print_usage()

if __name__ == "__main__":
    main() 