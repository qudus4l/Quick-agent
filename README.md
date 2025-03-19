# QuickAgent Dashboard

A modern web dashboard for the QuickAgent appointment management system. This application allows you to manage appointments, trigger reminder calls, and view call history in a clean, minimalistic interface.

## Features

- **Real-time Dashboard**: View key metrics and upcoming appointments
- **Appointment Management**: List, search, and view detailed appointment information
- **Call Management**: Trigger outbound reminder calls directly from the interface
- **Call History**: View detailed history of all inbound and outbound calls

## Tech Stack

### Backend
- Flask REST API
- SQLite database
- Twilio integration for calls and SMS

### Frontend
- React
- Material-UI for the component library
- Axios for API requests
- React Router for navigation

## Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn
- Twilio account with a phone number
- ngrok for testing (optional)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
OPENAI_API_KEY=your_openai_api_key
DEEPGRAM_API_KEY=your_deepgram_api_key
PUBLIC_URL=your_public_url_for_webhooks (e.g., your ngrok URL)
```

## Installation and Setup

### Backend Setup

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the API server:
   ```
   python api_server.py
   ```

3. The API server will start on http://localhost:5001

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install the dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. The React app will start on http://localhost:3000

## Testing the Twilio Integration

1. Run the Twilio handler:
   ```
   python twilio_handler.py
   ```

2. Use ngrok to expose your local server:
   ```
   ngrok http 5000
   ```

3. Update your Twilio phone number's webhook URL with the ngrok URL.

4. Start the appointment reminder scheduler:
   ```
   python appointment_reminder.py schedule
   ```

## Building for Production

1. Build the React app:
   ```
   cd frontend
   npm run build
   ```

2. The build files will be placed in the `frontend/build` directory, which is served by the Flask app.

3. Run the API server in production mode:
   ```
   python api_server.py
   ```

## Running Everything at Once

For convenience, you can run all the services at once using separate terminal windows:

1. Twilio handler: `python twilio_handler.py`
2. API server: `python api_server.py`
3. Appointment reminder: `python appointment_reminder.py schedule`

```
python3 QuickAgent.py