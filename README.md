# QuickAgent - AI Appointment Management System

QuickAgent is an innovative appointment management system that combines a conversational AI assistant with automated appointment scheduling and reminders. The system allows clients to book appointments through phone calls while providing businesses with a comprehensive dashboard to manage appointments and call history.

## Features

- **Conversational AI Assistant**: Handles incoming calls to schedule appointments
- **Automated Reminders**: Calls clients before their appointments
- **Dashboard Interface**: Manage appointments and call history
- **Test Tools**: Test the system functionality

## System Requirements

- Python 3.7+
- Node.js 14+
- NPM 6+
- Twilio Account (for phone functionality)

## Installation

### Backend Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/quickagent.git
   cd quickagent
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your Twilio credentials:
   ```
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   TEST_CLIENT_PHONE=your_test_client_phone
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Build the frontend:
   ```
   npm run build
   ```

## Running the Application

### Start the API Server

```
python api_server.py
```

The API server will start on http://localhost:5001.

### Start the React Development Server (for development)

```
cd frontend
npm start
```

The frontend development server will start on http://localhost:3000.

### Setting up Twilio for Inbound Calls

1. Start a tunnel to your local server using ngrok:
   ```
   ngrok http 5000
   ```

2. Configure your Twilio phone number to use the ngrok URL for Voice Webhook:
   - Go to the Twilio Console > Phone Numbers > Manage > Active Numbers
   - Select your number
   - Under "Voice & Fax" > "A Call Comes In", set the webhook to:
     ```
     [your-ngrok-url]/voice
     ```

## Running the Appointment Reminder System

To schedule automated reminders:

```
python appointment_reminder.py schedule
```

This will check for upcoming appointments every 15 minutes and send reminder calls 1 day before and 30 minutes before each appointment.

## Deployment

### Local Deployment

1. Build the frontend:
   ```
   cd frontend
   npm run build
   ```

2. Start the API server:
   ```
   python api_server.py
   ```

3. Access the application at http://localhost:5001

### AWS Deployment

A deployment script is included to help deploy to AWS:

1. Make the script executable:
   ```
   chmod +x deploy_aws.sh
   ```

2. Run the deployment script:
   ```
   ./deploy_aws.sh path/to/your-aws-key.pem ec2-user@your-instance-ip
   ```

3. Follow the instructions in the DEPLOY_INSTRUCTIONS.md file created on your AWS instance.

## Project Structure

- `api_server.py` - Main API server handling frontend requests
- `twilio_handler.py` - Twilio webhook handlers
- `QuickAgent.py` - Conversational AI implementation
- `appointment_manager.py` - Appointment database operations
- `appointment_reminder.py` - Automated reminder system
- `frontend/` - React frontend application

## Testing

### Test the Conversational AI

1. Call your Twilio phone number
2. Speak with the assistant to book an appointment

### Test Automated Reminders

1. Add a test appointment that's coming up soon
2. Run the reminder system in manual mode:
   ```
   python appointment_reminder.py
   ```

### Test via the Dashboard

1. Go to the Test page in the dashboard
2. Use the "Call Agent" button to call the Twilio number
3. Use the "Have Agent Call Client" button to test outbound calls

## Troubleshooting

### API Connection Issues

If your frontend can't connect to the API:

1. Check that the API server is running
2. Verify the API URL configuration in `frontend/src/config.js`
3. Check for CORS issues in browser developer tools

### Twilio Call Issues

1. Verify your Twilio credentials in the `.env` file
2. Check if your ngrok tunnel is running and the URL is correctly configured in Twilio
3. Verify that the webhook route is correctly set up

## License

This project is licensed under the MIT License - see the LICENSE file for details.
