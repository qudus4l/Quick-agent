# QuickAgent - Appointment Management System

QuickAgent is an intelligent appointment management system that integrates conversational AI with appointment scheduling, reminders, and management. This README explains how to set up, run, and test the system.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Setup](#setup)
3. [Running the Application](#running-the-application)
4. [Testing Locally](#testing-locally)
5. [Twilio Integration](#twilio-integration)
6. [Project Structure](#project-structure)
7. [Troubleshooting](#troubleshooting)

## Project Overview

QuickAgent provides:

- **Conversational AI Interface**: Natural language appointment booking and management
- **Voice & SMS Interactions**: Via Twilio integration
- **Automated Reminders**: Personalized reminder calls before appointments
- **Web Dashboard**: For appointment management and call history

## Setup

### Prerequisites

- Python 3.10+
- Twilio account (optional for local testing)
- OpenAI API key
- SQLite3 (included in Python)

### Installation

1. Clone the repository or ensure all files are in place

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables by creating a `.env` file:
   ```
   # OpenAI API Key
   OPENAI_API_KEY = "your_openai_api_key"
   
   # Twilio (optional for production use)
   TWILIO_ACCOUNT_SID = "your_twilio_account_sid"
   TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
   TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
   
   # For local testing
   TEST_CLIENT_PHONE = "your_phone_number"
   
   # Public URL (for Twilio webhooks)
   PUBLIC_URL = "your_ngrok_or_public_url"
   ```

## Running the Application

### Starting the Core System

1. **Run the API Server**:
   ```bash
   python api_server.py
   ```
   This will start the API server on port 5001.

2. **Run the Web Frontend** (if applicable):
   ```bash
   cd frontend
   npm start
   ```
   This will start the React frontend on port 3000.

3. **Run the Twilio Handler** (for voice/SMS interactions):
   ```bash
   python twilio_handler.py
   ```
   This will start the Twilio webhook handler on port 5000.

4. **Run the Interactive Conversation Mode**:
   ```bash
   python QuickAgent.py
   ```
   This allows you to directly test the conversational AI interface.

### Running the Appointment Reminder System

For automatic appointment reminders:

```bash
python appointment_reminder.py schedule
```

This will run in a continuous mode, checking for appointments every 15 minutes and sending reminders:
- One day before appointments
- 30 minutes before appointments

To manually trigger a reminder for a specific appointment:

```bash
python appointment_reminder.py remind <appointment_id>
```

Where `<appointment_id>` is the ID of the appointment you want to send a reminder for.

## Testing Locally

### Testing the Reminder System Without Twilio

You can test the appointment reminder system locally without actually making Twilio calls using the provided test scripts:

1. **General Test (Uses First Appointment)**:
   ```bash
   python test_reminder_assistant.py
   ```
   This uses the first appointment in the database.

2. **Test Specific Appointment**:
   ```bash
   python test_specific_reminder.py <appointment_id> <reminder_type>
   ```
   Example: `python test_specific_reminder.py 1 day_before`

3. **Improved Test (Recommended)**:
   ```bash
   python test_reminder_improved.py <appointment_id> <reminder_type>
   ```

Available reminder types:
- `day_before`: Reminder sent one day before appointment
- `thirty_min_before`: Reminder sent 30 minutes before appointment
- `general`: General appointment reminder

### Simulating a Conversation

The testing scripts provide an interactive console for simulating conversations:

1. The system will show the appointment details and initial greeting
2. Type your responses as if you were the client
3. The system will process and display what actions would be taken
4. Type 'exit', 'quit', or 'bye' to end the test

### Viewing Appointments

To view all appointments in the database:

```bash
python QuickAgent.py list
```

To view appointments for a specific name:

```bash
python QuickAgent.py list name "John Doe"
```

## Twilio Integration

### Setting Up Twilio (For Production)

1. Create a Twilio account and get a phone number
2. Update your `.env` file with Twilio credentials
3. Expose your local server using ngrok:
   ```bash
   ngrok http 5000
   ```
4. Configure your Twilio phone number in the Twilio dashboard:
   - Voice Webhook: `https://your-ngrok-url/voice` (HTTP POST)
   - SMS Webhook: `https://your-ngrok-url/sms` (HTTP POST)

For detailed Twilio setup instructions, see the `TWILIO_SETUP.md` file.

## Project Structure

- `QuickAgent.py`: Core conversational AI and database functions
- `appointment_reminder.py`: Automated reminder system
- `twilio_handler.py`: Handles Twilio voice and SMS interactions
- `api_server.py`: RESTful API for web dashboard
- `frontend/`: Web dashboard (React)
- `test_*.py`: Local testing scripts

## Troubleshooting

### Common Issues

1. **LLM Response Issues**: If the LLM produces unexpected responses in local testing, try adjusting the prompts in the test scripts.

2. **Database Issues**: If you encounter database errors, you might need to update the schema:
   ```bash
   sqlite3 appointments.db "ALTER TABLE appointments ADD COLUMN phone_number TEXT;"
   ```

3. **Environment Variables**: Ensure your `.env` file is correctly set up with all required variables.

4. **Twilio Authentication Errors**: Double-check your Twilio credentials and ensure your ngrok URL is correctly set in the Twilio dashboard.

### Getting Help

For detailed instructions on specific components, refer to:
- `TWILIO_SETUP.md` for Twilio integration
- `REMINDER_SETUP.md` for appointment reminder configuration

## License

This project is licensed under the MIT License. 