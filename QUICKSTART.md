# QuickAgent QuickStart Guide

This guide contains the essential commands you need to run and test QuickAgent locally.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Ensure your `.env` file has at least:
   ```
   OPENAI_API_KEY = "your_openai_api_key"
   ```

## Running the System

### Core components:

```bash
# Start the API server (port 5001)
python api_server.py

# Start the Twilio handler (port 5000)
python twilio_handler.py

# Start the web frontend
cd frontend && npm start
```

### Running the conversational interface:

```bash
# Interactive conversation
python QuickAgent.py
```

## Testing Appointment Reminders Locally

Use the improved test script to simulate conversations without making actual Twilio calls:

```bash
# Test a specific appointment with a specific reminder type
python test_reminder_improved.py <appointment_id> <reminder_type>

# Examples:
python test_reminder_improved.py 1 day_before
python test_reminder_improved.py 2 thirty_min_before
python test_reminder_improved.py 3 general
```

## Managing Appointments

```bash
# List all appointments
python QuickAgent.py list

# List appointments for a specific name
python QuickAgent.py list name "John Doe"

# Schedule automatic appointment reminders
python appointment_reminder.py schedule

# Manually trigger a reminder
python appointment_reminder.py remind <appointment_id>
```

## Database Management

If you need to update the database schema:

```bash
# Add phone_number column to appointments table
sqlite3 appointments.db "ALTER TABLE appointments ADD COLUMN phone_number TEXT;"

# Check appointments table contents
sqlite3 appointments.db "SELECT id, name, appointment_time FROM appointments"
```

For more detailed instructions, see the full `QUICKAGENT_README.md`. 