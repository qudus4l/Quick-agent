#!/bin/bash
# Script to update environment variables on AWS

# Make the script executable with: chmod +x update_aws_env.sh
# Run it with: ./update_aws_env.sh

# Set these variables to match your AWS environment
AWS_INSTANCE_IP="your-instance-ip"
SSH_KEY_PATH="path-to-your-ssh-key.pem"
APP_DIR="/path/to/app/directory"

# Optional: Check if required command-line tools are installed
if ! command -v ssh &> /dev/null; then
    echo "Error: ssh is not installed or not in PATH"
    exit 1
fi

echo "Updating environment variables on AWS instance $AWS_INSTANCE_IP..."

# Create a temporary .env file with production settings
cat > .env.aws << EOF
# Production environment settings for AWS
ENVIRONMENT=production
ALLOWED_ORIGINS=*

# OpenAI API Key
OPENAI_API_KEY="${OPENAI_API_KEY}"

# Twilio Credentials
TWILIO_ACCOUNT_SID="${TWILIO_ACCOUNT_SID}"
TWILIO_AUTH_TOKEN="${TWILIO_AUTH_TOKEN}"
TWILIO_PHONE_NUMBER="${TWILIO_PHONE_NUMBER}"

# Appointment Reminder Settings
PUBLIC_URL="${PUBLIC_URL}"
TEST_CLIENT_PHONE="${TEST_CLIENT_PHONE}"
EOF

# Copy the .env file to the AWS instance
echo "Copying .env file to AWS..."
scp -i "$SSH_KEY_PATH" .env.aws "$AWS_INSTANCE_IP:$APP_DIR/.env"

# Remove the temporary file
rm .env.aws

# Restart the services on AWS
echo "Restarting services on AWS..."
ssh -i "$SSH_KEY_PATH" "$AWS_INSTANCE_IP" << EOF
  cd $APP_DIR
  # Stop any existing processes
  pkill -f "python3 api_server.py" || echo "No api_server.py processes running"
  pkill -f "python3 twilio_handler.py" || echo "No twilio_handler.py processes running"
  
  # Start services
  nohup python3 api_server.py > api_server.log 2>&1 &
  nohup python3 twilio_handler.py > twilio_handler.log 2>&1 &
  
  echo "Services restarted. Logs available in api_server.log and twilio_handler.log"
EOF

echo "AWS environment update completed!" 