#!/bin/bash
# Mary Bird Perkins GearVue Deployment Script
# This script automates the deployment of GearVue to the MBP server at 172.30.98.21:7373

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "  ███╗   ███╗██████╗ ██████╗      ██████╗ ███████╗ █████╗ ██████╗ ██╗   ██╗██╗   ██╗███████╗"
echo "  ████╗ ████║██╔══██╗██╔══██╗    ██╔════╝ ██╔════╝██╔══██╗██╔══██╗██║   ██║██║   ██║██╔════╝"
echo "  ██╔████╔██║██████╔╝██████╔╝    ██║  ███╗█████╗  ███████║██████╔╝██║   ██║██║   ██║█████╗  "
echo "  ██║╚██╔╝██║██╔══██╗██╔═══╝     ██║   ██║██╔══╝  ██╔══██║██╔══██╗╚██╗ ██╔╝██║   ██║██╔══╝  "
echo "  ██║ ╚═╝ ██║██████╔╝██║         ╚██████╔╝███████╗██║  ██║██║  ██║ ╚████╔╝ ╚██████╔╝███████╗"
echo "  ╚═╝     ╚═╝╚═════╝ ╚═╝          ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝   ╚═════╝ ╚══════╝"
echo "                                                                                            "
echo " Equipment Tracker - Mary Bird Perkins Deployment (172.30.98.21:7373)                       "
echo -e "${NC}"
echo "================================================================================="

# Check if running with proper permissions
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}Warning: This script may need sudo privileges to bind to port 7373${NC}"
  read -p "Continue without sudo? (y/N): " continue_without_sudo
  if [[ ! $continue_without_sudo =~ ^[Yy]$ ]]; then
    echo "Restarting with sudo..."
    exec sudo "$0" "$@"
    exit $?
  fi
fi

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

# Set MBP-specific environment variables
echo -e "${YELLOW}Setting up Mary Bird Perkins environment...${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env.mbp" ]; then
    echo "Creating .env.mbp file with MBP-specific settings..."
    
    # Prompt for SMTP credentials if needed
    read -p "SMTP username for notifications (default: gearvue@marybird.com): " MAIL_USERNAME
    MAIL_USERNAME=${MAIL_USERNAME:-gearvue@marybird.com}
    
    # Read password securely 
    read -sp "SMTP password: " MAIL_PASSWORD
    echo
    
    # Create .env.mbp file
    cat > .env.mbp <<EOL
# Mary Bird Perkins GearVue Environment Variables
# Generated on $(date)

# Application Settings
APPLICATION_URL=http://172.30.98.21:7373
TZ=America/Chicago

# Mail Settings
MAIL_SERVER=smtp.marybird.com
MAIL_PORT=587
MAIL_USERNAME=$MAIL_USERNAME
MAIL_PASSWORD=$MAIL_PASSWORD
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=gearvue@marybird.com
EOL
    
    echo -e "${GREEN}Created .env.mbp file with MBP settings${NC}"
else
    echo -e "${YELLOW}.env.mbp file already exists. Using existing configuration.${NC}"
fi

# Ensure directories exist
echo -e "${BLUE}Creating required directories...${NC}"
mkdir -p logs output Resources

# Check if we need to update the existing deployment
if docker ps | grep -q "mbp-gearvue-app"; then
    echo -e "${YELLOW}Existing deployment detected.${NC}"
    read -p "Update existing deployment? (Y/n): " UPDATE_DEPLOYMENT
    
    if [[ ! $UPDATE_DEPLOYMENT =~ ^[Nn]$ ]]; then
        echo -e "${BLUE}Updating deployment...${NC}"
        docker-compose -f docker-compose.mbp.yml down
        docker-compose -f docker-compose.mbp.yml --env-file .env.mbp up -d --build
        
        echo -e "${GREEN}Deployment updated!${NC}"
        echo -e "GearVue is now running at: ${BLUE}http://172.30.98.21:7373${NC}"
        exit 0
    fi
fi

# Start from scratch
echo -e "${BLUE}Starting deployment process...${NC}"

# Pull the latest code if needed
if [ -d ".git" ]; then
    read -p "Pull latest code from repository? (Y/n): " PULL_CODE
    if [[ ! $PULL_CODE =~ ^[Nn]$ ]]; then
        echo "Pulling latest code..."
        git pull
    fi
fi

# Build and start the containers
echo -e "${BLUE}Building and starting containers...${NC}"
docker-compose -f docker-compose.mbp.yml --env-file .env.mbp up -d --build

# Check if the application started successfully
sleep 5
if docker-compose -f docker-compose.mbp.yml ps | grep "mbp-gearvue-app" | grep -q "Up"; then
    echo -e "${GREEN}GearVue has been successfully deployed!${NC}"
    echo -e "The application is now running at: ${BLUE}http://172.30.98.21:7373${NC}"
else
    echo -e "${RED}There was an issue starting the application.${NC}"
    echo "Check the logs with: docker-compose -f docker-compose.mbp.yml logs"
fi

echo -e "${GREEN}Deployment script completed.${NC}"
echo "================================================================================="
echo "Useful commands:"
echo "  - View logs: docker-compose -f docker-compose.mbp.yml logs -f"
echo "  - Stop application: docker-compose -f docker-compose.mbp.yml down"
echo "  - Restart application: docker-compose -f docker-compose.mbp.yml restart"
echo "  - Manual update: docker exec mbp-gearvue-app /app/update.sh"
echo "================================================================================="