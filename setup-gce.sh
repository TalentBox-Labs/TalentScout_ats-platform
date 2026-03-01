#!/bin/bash

# Setup script for GCP Compute Engine instance
# Run this on your GCE instance to prepare it for deployment

echo "Setting up GCP Compute Engine instance for TalentScout deployment..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/talentscout
sudo chown $USER:$USER /opt/talentscout

# Copy production docker-compose file (you'll need to upload this)
# scp docker-compose.prod.yml user@instance:/opt/talentscout/
# scp setup-gce.sh user@instance:/opt/talentscout/  # Optional: upload this script too

echo "Please upload docker-compose.prod.yml to /opt/talentscout/ on your instance"
echo "You can use: scp docker-compose.prod.yml user@your-instance-ip:/opt/talentscout/"

# Create data directories for persistence (optional)
sudo mkdir -p /opt/talentscout/data/postgres
sudo mkdir -p /opt/talentscout/data/redis
sudo chown -R 999:999 /opt/talentscout/data/postgres  # postgres user
sudo chown -R 100:101 /opt/talentscout/data/redis    # redis user

# Install gcloud CLI (if not already installed)
# curl https://sdk.cloud.google.com | bash
# exec -l $SHELL

echo "Setup complete! Please:"
echo "1. Upload docker-compose.prod.yml to /opt/talentscout/"
echo "2. Configure environment variables in the deployment workflow"
echo "3. Ensure firewall rules allow ports 8000 and 3000"
echo "4. Test the deployment"