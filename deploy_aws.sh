#!/bin/bash

# QuickAgent AWS Deployment Script
# This script helps update your AWS EC2 instance with the latest version of the application

# Exit on error
set -e

echo "====== QuickAgent AWS Deployment Script ======"

# Check if SSH key is provided
if [ -z "$1" ]; then
  echo "Error: Please provide the path to your AWS SSH key"
  echo "Usage: ./deploy_aws.sh path/to/key.pem [ec2-user@your-instance-ip]"
  exit 1
fi

# Set the SSH key
SSH_KEY="$1"

# Check if instance address is provided, otherwise use default
if [ -z "$2" ]; then
  INSTANCE="ec2-user@your-ec2-instance-ip"
  echo "No instance address provided, using default: $INSTANCE"
  echo "Consider updating with your actual EC2 instance address"
else
  INSTANCE="$2"
fi

echo "Using SSH key: $SSH_KEY"
echo "Deploying to: $INSTANCE"

# Create a temporary directory for deployment files
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Copy necessary files
echo "Copying deployment files..."
cp -r api_server.py QuickAgent.py appointment_manager.py appointment_reminder.py requirements.txt twilio_handler.py $TEMP_DIR/
cp -r frontend/build $TEMP_DIR/

# Create a .env file with production settings
cat > $TEMP_DIR/.env << EOF
# Production environment variables
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
TEST_CLIENT_PHONE=your_test_client_phone
EOF

echo "Created environment file with placeholders. Update with your actual values."

# Create deployment instructions
cat > $TEMP_DIR/DEPLOY_INSTRUCTIONS.md << EOF
# QuickAgent Deployment Instructions

## Backend Setup
1. Install required packages: \`pip install -r requirements.txt\`
2. Update the .env file with your actual Twilio credentials
3. Start the API server: \`python api_server.py\`

## Frontend Setup
The frontend build is already included in the \`build\` directory.

## Serving with Nginx (Recommended)
1. Install Nginx: \`sudo amazon-linux-extras install nginx1\`
2. Configure Nginx to serve the static frontend files and proxy API requests
3. Example config:
   ```
   server {
       listen 80;
       server_name your_domain.com;

       # Serve frontend static files
       location / {
           root /path/to/quickagent/frontend/build;
           try_files \$uri \$uri/ /index.html;
       }

       # Proxy API requests
       location /api/ {
           proxy_pass http://localhost:5001;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
       }
   }
   ```

## Running as a Service
To keep the API server running after logout, consider using:
- PM2: \`npm install -g pm2\` then \`pm2 start api_server.py --name quickagent-api\`
- Or create a systemd service file

## Updating Environment Variables
Edit the .env file in the application root directory with your actual credentials.
EOF

echo "Created deployment instructions"

# Create a simple script to update environment variables
cat > $TEMP_DIR/update_env.sh << EOF
#!/bin/bash
# Script to update environment variables

echo "Updating QuickAgent environment variables"

read -p "TWILIO_ACCOUNT_SID: " TWILIO_ACCOUNT_SID
read -p "TWILIO_AUTH_TOKEN: " TWILIO_AUTH_TOKEN
read -p "TWILIO_PHONE_NUMBER: " TWILIO_PHONE_NUMBER
read -p "TEST_CLIENT_PHONE: " TEST_CLIENT_PHONE

cat > .env << ENVFILE
TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN
TWILIO_PHONE_NUMBER=$TWILIO_PHONE_NUMBER
TEST_CLIENT_PHONE=$TEST_CLIENT_PHONE
ENVFILE

echo "Environment variables updated successfully!"
EOF

chmod +x $TEMP_DIR/update_env.sh
echo "Created environment variable update script"

# Zip the deployment package
DEPLOY_PACKAGE="quickagent_deploy.zip"
echo "Creating deployment package: $DEPLOY_PACKAGE"
(cd $TEMP_DIR && zip -r ../$DEPLOY_PACKAGE .)

echo "Deployment package created successfully"

# Ask before uploading to AWS
read -p "Upload deployment package to AWS instance? (y/n): " UPLOAD_CONFIRM

if [ "$UPLOAD_CONFIRM" = "y" ] || [ "$UPLOAD_CONFIRM" = "Y" ]; then
  echo "Uploading deployment package to AWS instance..."
  scp -i $SSH_KEY $DEPLOY_PACKAGE $INSTANCE:~
  
  echo "Executing remote deployment steps..."
  ssh -i $SSH_KEY $INSTANCE << REMOTE_COMMANDS
    echo "Received deployment package"
    mkdir -p quickagent
    unzip -o quickagent_deploy.zip -d quickagent
    cd quickagent
    chmod +x update_env.sh
    echo "Deployment files extracted. See DEPLOY_INSTRUCTIONS.md for next steps."
REMOTE_COMMANDS

  echo "Deployment complete! Follow the instructions on your AWS instance."
else
  echo "Upload skipped. You can manually transfer $DEPLOY_PACKAGE to your AWS instance."
fi

# Cleanup
echo "Cleaning up temporary files..."
rm -rf $TEMP_DIR

echo "====== Deployment script completed ======"
echo "Your deployment package is available at: $DEPLOY_PACKAGE" 