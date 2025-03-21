#!/usr/bin/env python3
"""
Run Twilio Handler with SSL Support

This script runs the Twilio webhook handler with SSL/TLS support,
which is required for Twilio webhooks in production.

Usage:
  python run_with_ssl.py

Requirements:
  - OpenSSL certificate and key files
  - Python Flask and Twilio packages
"""

import os
import sys
from dotenv import load_dotenv
from twilio_handler import app

# Load environment variables
load_dotenv()

def generate_self_signed_cert():
    """Generate a self-signed SSL certificate if none exists."""
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        print("Generating self-signed SSL certificate...")
        os.system('openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost"')
        print("Self-signed certificate generated.")

def main():
    # Check if certificates exist or generate them
    generate_self_signed_cert()
    
    # Get host and port from environment or use defaults
    host = os.getenv('TWILIO_HANDLER_HOST', '0.0.0.0')
    port = int(os.getenv('TWILIO_HANDLER_PORT', 5002))
    
    # Update the server base URL environment variable
    server_base_url = os.getenv('SERVER_BASE_URL')
    if not server_base_url:
        print("Warning: SERVER_BASE_URL not set in .env file.")
        print("Twilio callbacks may not work correctly without this.")
        print("Set SERVER_BASE_URL to your public-facing URL (e.g., https://your-domain.com)")
    
    print(f"Starting Twilio webhook handler with SSL on {host}:{port}...")
    print("Webhooks will be available at:")
    print(f"  Voice: {server_base_url}/voice")
    print(f"  SMS: {server_base_url}/sms")
    
    # Run the Flask app with SSL
    app.run(
        host=host,
        port=port,
        ssl_context=('cert.pem', 'key.pem'),
        debug=False  # Set to False in production
    )

if __name__ == "__main__":
    main() 