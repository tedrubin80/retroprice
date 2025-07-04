#!/bin/bash

# Film Price Guide - Dreamhost Deployment Script

echo "🚀 Deploying Film Price Guide to Dreamhost..."

# Configuration
REMOTE_USER="your-dreamhost-user"
REMOTE_HOST="your-domain.com"
REMOTE_PATH="/home/$REMOTE_USER/your-domain.com"
LOCAL_PATH="./public"

# Upload files via SFTP
echo "📤 Uploading files..."
rsync -avz --delete \
    --exclude '.git' \
    --exclude '.env' \
    --exclude 'node_modules' \
    --exclude 'logs' \
    --exclude '.DS_Store' \
    $LOCAL_PATH/ $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/

echo "✅ Deployment complete!"
echo "🌐 Visit: https://$REMOTE_HOST"
