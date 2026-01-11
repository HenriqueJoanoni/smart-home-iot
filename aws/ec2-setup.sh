#!/bin/bash

###############################################
# Smart Home IoT - EC2 Setup Script
# Installs Docker, Docker Compose, and dependencies
###############################################

set -e

echo "================================================"
echo "  Smart Home IoT - EC2 Setup"
echo "================================================"

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
echo "🐙 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install Git
echo "📚 Installing Git..."
sudo yum install -y git

# Install utilities
echo "🔧 Installing utilities..."
sudo yum install -y htop curl wget nano

# Create app directory
echo "📁 Creating application directory..."
sudo mkdir -p /opt/smart-home-iot
sudo chown ec2-user: ec2-user /opt/smart-home-iot

# Configure firewall (Security Group should handle this, but just in case)
echo "🔥 Configuring firewall..."
sudo yum install -y firewalld || true
if systemctl is-active --quiet firewalld; then
    sudo firewall-cmd --permanent --add-service=http
    sudo firewall-cmd --permanent --add-service=https
    sudo firewall-cmd --reload
fi

echo "✅ EC2 Setup Complete!"
echo ""
echo "⚠️  IMPORTANT: Log out and log back in for Docker group changes to take effect!"
echo "   Run: exit"
echo "   Then reconnect via SSH"
echo ""
echo "Next steps:"
echo "1. Clone your repository"
echo "2. Configure .env files"
echo "3. Run: cd /opt/smart-home-iot && ./aws/scripts/deploy.sh"