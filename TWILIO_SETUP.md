# Setting Up Twilio with QuickAgent

This guide will walk you through the process of setting up Twilio to work with your QuickAgent application, allowing users to interact with your appointment booking system via phone calls and SMS.

## Prerequisites

1. A Twilio account (you can sign up for a free trial at [twilio.com](https://www.twilio.com))
2. The QuickAgent application with the Twilio integration
3. ngrok or a similar tool to expose your local server to the internet

## Step 1: Install Required Packages

Make sure you have all the required packages installed:

```bash
pip install -r requirements.txt
```

## Step 2: Set Up Your Twilio Account

1. Sign up for a Twilio account at [twilio.com](https://www.twilio.com) if you haven't already.
2. Once logged in, navigate to the Twilio Console dashboard.
3. Note your Account SID and Auth Token (you'll need these for your .env file).

## Step 3: Get a Twilio Phone Number

1. In the Twilio Console, go to "Phone Numbers" > "Manage" > "Buy a Number".
2. Search for a phone number with voice and SMS capabilities.
3. Purchase a number (it's free with a trial account).
4. Note down this phone number (you'll need it for your .env file).

## Step 4: Update Your .env File

Update your `.env` file with your Twilio credentials:

```
TWILIO_ACCOUNT_SID = "your_account_sid_here"
TWILIO_AUTH_TOKEN = "your_auth_token_here"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number_here"
```

Replace the placeholder values with your actual Twilio credentials.

## Step 5: Expose Your Local Server

To allow Twilio to communicate with your application, you need to expose your local server to the internet. You can use ngrok for this:

1. Download and install ngrok from [ngrok.com](https://ngrok.com/).
2. Start your Twilio handler:

```bash
python twilio_handler.py
```

3. In a separate terminal, start ngrok to expose port 5000:

```bash
ngrok http 5000
```

4. Note the HTTPS URL provided by ngrok (e.g., `https://a1b2c3d4.ngrok.io`).

## Step 6: Configure Your Twilio Phone Number

1. In the Twilio Console, go to "Phone Numbers" > "Manage" > "Active Numbers".
2. Click on your phone number to configure it.
3. Under "Voice & Fax" > "A Call Comes In", select "Webhook" and enter:
   - URL: `https://your-ngrok-url/voice` (replace with your actual ngrok URL)
   - Method: HTTP POST
4. Under "Messaging" > "A Message Comes In", select "Webhook" and enter:
   - URL: `https://your-ngrok-url/sms` (replace with your actual ngrok URL)
   - Method: HTTP POST
5. Click "Save" at the bottom of the page.

## Step 7: Test Your Integration

1. Call your Twilio phone number.
2. You should hear the QuickAgent greeting and be able to interact with it via voice.
3. Try sending an SMS to your Twilio phone number.
4. You should receive a response from QuickAgent.

## How It Works

When someone calls or texts your Twilio number:

1. Twilio sends a webhook to your application.
2. Your application processes the input using the language model.
3. The response is converted to TwiML (Twilio Markup Language).
4. Twilio receives the TwiML and executes the instructions (e.g., speaking text, gathering input).

## Troubleshooting

- **Webhook errors**: Check your ngrok URL and make sure it's correctly configured in Twilio.
- **No response**: Ensure your `twilio_handler.py` is running and your .env file has the correct credentials.
- **Speech recognition issues**: Try speaking clearly and in a quiet environment.

## Going to Production

For a production environment:

1. Deploy your application to a cloud provider (AWS, Heroku, etc.).
2. Use a proper domain name instead of ngrok.
3. Set up SSL for secure communication.
4. Consider implementing authentication for your webhooks.

## Additional Resources

- [Twilio Python Documentation](https://www.twilio.com/docs/libraries/python)
- [Twilio TwiML Documentation](https://www.twilio.com/docs/voice/twiml)
- [Twilio Voice API Documentation](https://www.twilio.com/docs/voice/api)
- [Twilio SMS API Documentation](https://www.twilio.com/docs/sms/api) 