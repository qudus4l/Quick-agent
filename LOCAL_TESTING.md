# Testing Appointment Reminders Locally

This guide explains how to test the QuickAgent appointment reminder system locally without requiring Twilio or making actual phone calls.

## Prerequisites

Ensure you have:
- Python 3.10+ installed
- OpenAI API key in your `.env` file
- QuickAgent dependencies installed (`pip install -r requirements.txt`)

## Testing Scripts Overview

QuickAgent provides three scripts for local testing:

1. **test_reminder_assistant.py**: Basic test that uses the first appointment in the database
2. **test_specific_reminder.py**: Test a specific appointment with configurable reminder type
3. **test_reminder_improved.py**: Enhanced test with better role separation (RECOMMENDED)

## Recommended Testing Method

Use the improved test script for the most accurate simulation:

```bash
python test_reminder_improved.py <appointment_id> <reminder_type>
```

### Parameters:

- `<appointment_id>`: ID of the appointment to test (1, 2, 3, etc.)
- `<reminder_type>`: Type of reminder to simulate
  - `day_before`: One day before the appointment
  - `thirty_min_before`: 30 minutes before the appointment
  - `general`: Generic reminder without specific timing

### Examples:

```bash
# Test appointment ID 1 with a day-before reminder
python test_reminder_improved.py 1 day_before

# Test appointment ID 2 with a 30-minute reminder
python test_reminder_improved.py 2 thirty_min_before

# Test appointment ID 3 with a general reminder
python test_reminder_improved.py 3 general
```

## How the Test Works

1. The script loads the appointment from the database
2. It creates a reminder context similar to what would be created in a real call
3. It generates the same initial greeting that would be used in a real call
4. You can type responses as if you were the client receiving the call
5. The system processes your responses and shows:
   - The assistant's responses
   - What actions would be taken (confirm, reschedule, cancel)
   - System messages indicating database changes that would occur

## Testing Different Scenarios

### Confirming an Appointment:
Respond with phrases like "Yes, I'll be there" or "I confirm"

### Rescheduling an Appointment:
Respond with phrases like "I need to reschedule" or "Can we change the time?"

### Canceling an Appointment:
Respond with phrases like "I need to cancel" or "I can't make it"

### Ending the Test:
Type 'exit', 'quit', or 'bye' to end the test conversation

## Viewing Appointments

Before testing, you may want to check what appointments are available:

```bash
# View all appointments
python QuickAgent.py list

# View appointments for a specific name
python QuickAgent.py list name "John"
```

## Adding Test Appointments

If you need to add test appointments, you can use:

```bash
# Run the interactive conversational interface
python QuickAgent.py
```

Then interact with the assistant to book a new appointment.

## Troubleshooting

- **No appointments found**: Make sure you have appointments in your `appointments.db` file
- **LLM response issues**: Check that your OpenAI API key is valid
- **Schema errors**: You may need to add the phone_number column:
  ```bash
  sqlite3 appointments.db "ALTER TABLE appointments ADD COLUMN phone_number TEXT;"
  ```

This local testing approach allows you to thoroughly test the conversational flow without incurring Twilio charges or making actual phone calls. 