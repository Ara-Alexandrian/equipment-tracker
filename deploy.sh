#!/bin/bash
# GearVue Equipment Tracker Deployment Script
# This script handles the configuration and deployment of the GearVue application

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "  ██████  ███████  █████  ██████  ██    ██ ██    ██ ███████ "
echo " ██       ██      ██   ██ ██   ██ ██    ██ ██    ██ ██      "
echo " ██   ███ █████   ███████ ██████  ██    ██ ██    ██ █████   "
echo " ██    ██ ██      ██   ██ ██   ██  ██  ██  ██    ██ ██      "
echo "  ██████  ███████ ██   ██ ██   ██   ████    ██████  ███████ "
echo "                                                            "
echo " Equipment Tracker - Deployment Script                      "
echo -e "${NC}"
echo "============================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker before continuing: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed.${NC}"
    echo "Please install Docker Compose before continuing: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    
    # Prompt for environment variables
    read -p "Application port (default: 5000): " PORT
    PORT=${PORT:-5000}
    
    read -p "SMTP server address (default: smtp.example.com): " MAIL_SERVER
    MAIL_SERVER=${MAIL_SERVER:-smtp.example.com}
    
    read -p "SMTP server port (default: 587): " MAIL_PORT
    MAIL_PORT=${MAIL_PORT:-587}
    
    read -p "SMTP username: " MAIL_USERNAME
    
    # Read password securely 
    read -sp "SMTP password: " MAIL_PASSWORD
    echo
    
    read -p "Mail default sender (default: equipment-tracker@example.com): " MAIL_DEFAULT_SENDER
    MAIL_DEFAULT_SENDER=${MAIL_DEFAULT_SENDER:-equipment-tracker@example.com}
    
    read -p "Use TLS for SMTP? (Y/n): " USE_TLS
    if [[ $USE_TLS == "n" || $USE_TLS == "N" ]]; then
        MAIL_USE_TLS=False
    else
        MAIL_USE_TLS=True
    fi
    
    # Get the server's public IP or allow user to specify URL
    echo -e "${YELLOW}Trying to determine server's public IP...${NC}"
    PUBLIC_IP=$(curl -s ifconfig.me || echo "localhost")
    
    read -p "Application URL (default: http://$PUBLIC_IP:$PORT): " APPLICATION_URL
    APPLICATION_URL=${APPLICATION_URL:-http://$PUBLIC_IP:$PORT}
    
    read -p "Timezone (default: America/Chicago): " TZ
    TZ=${TZ:-America/Chicago}
    
    # Create .env file
    cat > .env <<EOL
# GearVue Equipment Tracker Environment Variables
# Generated on $(date)

# Application Settings
PORT=$PORT
FLASK_ENV=production
APPLICATION_URL=$APPLICATION_URL
TZ=$TZ

# Mail Settings
MAIL_SERVER=$MAIL_SERVER
MAIL_PORT=$MAIL_PORT
MAIL_USERNAME=$MAIL_USERNAME
MAIL_PASSWORD=$MAIL_PASSWORD
MAIL_USE_TLS=$MAIL_USE_TLS
MAIL_DEFAULT_SENDER=$MAIL_DEFAULT_SENDER

# Docker Settings
TAG=latest
EOL
    
    echo -e "${GREEN}Created .env file with your settings${NC}"
else
    echo -e "${YELLOW}.env file already exists. Using existing configuration.${NC}"
    echo "To regenerate this file, delete it first and run this script again."
fi

# Ensure directories exist
echo -e "${BLUE}Creating required directories...${NC}"
mkdir -p logs output Resources traefik/config traefik/certificates

# Check if there's a backup to restore
if [ -d "backup" ] && [ -f "backup/app_data.tar.gz" ]; then
    read -p "Backup found. Do you want to restore it? (y/N): " RESTORE_BACKUP
    if [[ $RESTORE_BACKUP == "y" || $RESTORE_BACKUP == "Y" ]]; then
        echo -e "${YELLOW}Restoring backup...${NC}"
        # Extract backup to app/data directory
        mkdir -p app/data
        tar -xzf backup/app_data.tar.gz -C app/data
        echo -e "${GREEN}Backup restored.${NC}"
    fi
fi

# Offer to build and start containers
read -p "Do you want to build and start the application now? (Y/n): " START_APP
if [[ $START_APP == "n" || $START_APP == "N" ]]; then
    echo -e "${BLUE}Deployment prepared but not started.${NC}"
    echo "Run 'docker-compose up -d' to start the application when ready."
else
    echo -e "${BLUE}Building and starting containers...${NC}"
    docker-compose up --build -d
    
    # Check if the application started successfully
    sleep 5
    if docker-compose ps | grep "gearvue-app" | grep -q "Up"; then
        echo -e "${GREEN}GearVue Equipment Tracker is now running!${NC}"
        echo -e "Access the application at: ${BLUE}$(grep APPLICATION_URL .env | cut -d '=' -f2)${NC}"
    else
        echo -e "${RED}There was an issue starting the application.${NC}"
        echo "Check the logs with: docker-compose logs"
    fi
fi

echo -e "${GREEN}Deployment script completed.${NC}"
echo "============================================================"
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop application: docker-compose down"
echo "  - Restart application: docker-compose restart"
echo "  - Backup data: ./backup.sh"
echo "============================================================"