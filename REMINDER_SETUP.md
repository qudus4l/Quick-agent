# Appointment Reminder System

This guide explains how to set up and use the appointment reminder system to make outgoing calls to clients for appointment reminders.

## Overview

The appointment reminder system automatically calls clients before their scheduled appointments to remind them and allow them to confirm, reschedule, or cancel their appointments. It consists of:

1. An outgoing call system (`appointment_reminder.py`) that schedules and initiates calls
2. Webhook handlers in `twilio_handler.py` that process client responses during calls
3. Integration with your existing appointment database

## Prerequisites

1. Twilio account with valid credentials
2. Your QuickAgent application with the Twilio integration
3. A publicly accessible URL for your webhook handlers (e.g., using ngrok)

## Setup

### 1. Update Your .env File

Add the following to your `.env` file:

```
# Appointment Reminder Settings
PUBLIC_URL = "your_public_url_here"  # Your ngrok or public URL
TEST_CLIENT_PHONE = "+1XXXXXXXXXX"   # Your phone number to receive test calls
```

Example:
```
PUBLIC_URL = "https://a1b2c3d4.ngrok.io"
TEST_CLIENT_PHONE = "+15551234567"
```

### 2. Run Your Twilio Handler

Make sure your Twilio webhook handler is running and accessible via your public URL:

```bash
python twilio_handler.py
```

In a separate terminal, run ngrok to expose your server (if needed):

```bash
ngrok http 5000
```

### 3. Test the Reminder System

You can test the system by manually triggering a reminder for a specific appointment:

```bash
python appointment_reminder.py remind 1  # Replace '1' with actual appointment ID
```

Or through the web interface:

```
http://localhost:5000/make-test-call?id=1  # Replace '1' with actual appointment ID
```

### 4. Run the Scheduler

For automatic reminders, run the scheduler:

```bash
python appointment_reminder.py schedule
```

This will check for appointments that need reminders every 15 minutes. The scheduler will send:
- A reminder one day before the appointment
- A reminder one hour before the appointment

## How It Works

### Outgoing Calls Process:

1. The system checks the database for upcoming appointments
2. For appointments that match reminder criteria, it initiates an outgoing call
3. When the client answers, they hear their appointment details and options
4. The client can press:
   - 1 to confirm the appointment
   - 2 to reschedule (will instruct to call the office directly)
   - 3 to cancel (will instruct to call the office directly)

### Call Flow:

```
System: "Hello [Name]! This is a reminder about your appointment scheduled for [Time]...
         Press 1 to confirm, 2 to reschedule, or 3 to cancel."

Client: *presses 1*

System: "Thank you for confirming your appointment. We look forward to seeing you!"
```

## Customizing the System

### Reminder Timing

You can adjust when reminders are sent by modifying the `should_send_reminder` function in `appointment_reminder.py` or by setting environment variables:

```
REMINDER_DAYS_BEFORE = 1  # Days before appointment to send first reminder
REMINDER_HOURS_BEFORE = 1  # Hours before appointment to send second reminder
```

### Message Content

To change the message content, modify the appropriate sections in:
- `make_reminder_call` function in `appointment_reminder.py`
- `appointment_action` route in `twilio_handler.py`

### Adding More Actions

For a production system, you might want to:
1. Implement actual rescheduling functionality
2. Update the database when appointments are canceled
3. Send confirmation SMS after the call
4. Add more reminder times

## Troubleshooting

- **Call not connecting**: Check that your Twilio account has sufficient credit and that the phone number is correct
- **Webhook errors**: Ensure your public URL is correct and your Flask server is running
- **Timing issues**: Verify that the appointment times in your database can be properly parsed by the system

## Going to Production

For a production environment:

1. Deploy the application to a cloud provider
2. Use a proper domain name instead of ngrok
3. Implement proper authentication and security
4. Set up a more robust scheduling mechanism (e.g., using Celery or a cron job)
5. Add phone number storage to your appointment database
6. Implement proper logging and monitoring 