#!/bin/bash
# GearVue Equipment Tracker Restore Script
# This script restores application data from a backup

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}GearVue Equipment Tracker - Restore Script${NC}"
echo "============================================================"

# Check if a backup directory was specified
if [ $# -eq 0 ]; then
    # Check if latest backup exists
    if [ -d "backup/latest" ]; then
        BACKUP_DIR="backup/latest"
        echo -e "${YELLOW}No backup directory specified. Using latest backup.${NC}"
    else
        echo -e "${RED}Error: No backup directory specified and no latest backup found.${NC}"
        echo "Usage: $0 [backup directory]"
        echo "Example: $0 backup/2025-05-15"
        exit 1
    fi
else
    BACKUP_DIR="$1"
    # Check if the specified backup directory exists
    if [ ! -d "$BACKUP_DIR" ]; then
        echo -e "${RED}Error: Backup directory '$BACKUP_DIR' not found.${NC}"
        exit 1
    fi
fi

echo -e "${YELLOW}Restoring from backup: $BACKUP_DIR${NC}"

# Make sure the backup contains the necessary files
if [ ! -f "$BACKUP_DIR/app_data.tar.gz" ]; then
    echo -e "${RED}Error: Backup is incomplete or invalid.${NC}"
    echo "Could not find app_data.tar.gz in $BACKUP_DIR"
    exit 1
fi

# Warning and confirmation
echo -e "${RED}WARNING: This will replace all current data with the backup.${NC}"
echo -e "${RED}All existing data will be lost.${NC}"
read -p "Are you sure you want to continue? (y/N): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Restore cancelled."
    exit 0
fi

# Determine if the application is running in Docker
if docker ps | grep -q "gearvue-app"; then
    echo "Application is running in Docker."
    echo "Stopping containers..."
    docker-compose down
    
    # Clear existing volume and restore backup
    echo "Restoring data to Docker volume..."
    
    # Create a temporary container to access the volume data
    docker volume create gearvue_data
    CONTAINER_ID=$(docker create --name gearvue-restore-tmp -v gearvue_data:/data alpine:latest)
    
    # Start the container
    docker start $CONTAINER_ID
    
    # Extract backup data
    echo "Extracting backup..."
    mkdir -p temp_restore
    tar -xzf "$BACKUP_DIR/app_data.tar.gz" -C temp_restore
    
    # Copy data to container
    echo "Copying data to Docker volume..."
    docker cp temp_restore/app_data/. $CONTAINER_ID:/data/
    
    # Remove temporary files and container
    rm -rf temp_restore
    docker rm -f $CONTAINER_ID
    
    # Restart containers
    echo "Restarting application..."
    docker-compose up -d
else
    # Restore to local directory
    echo "Restoring to local data directory..."
    
    # Make sure the target directory exists
    mkdir -p app
    
    # Remove existing data directory if it exists
    if [ -d "app/data" ]; then
        echo "Removing existing data..."
        rm -rf app/data
    fi
    
    # Extract backup
    echo "Extracting backup..."
    tar -xzf "$BACKUP_DIR/app_data.tar.gz" -C app
fi

# Restore .env file if it exists in the backup
if [ -f "$BACKUP_DIR/.env.backup" ]; then
    echo "Restoring environment configuration..."
    cp "$BACKUP_DIR/.env.backup" .env
fi

# Restore logs if they exist in the backup and user wants to restore them
if [ -f "$BACKUP_DIR/logs.tar.gz" ]; then
    read -p "Do you want to restore logs as well? (y/N): " RESTORE_LOGS
    if [[ $RESTORE_LOGS =~ ^[Yy]$ ]]; then
        echo "Restoring logs..."
        tar -xzf "$BACKUP_DIR/logs.tar.gz"
    fi
fi

echo -e "${GREEN}Restore completed successfully!${NC}"
echo "Data has been restored from: $BACKUP_DIR"
echo "============================================================"
echo "You may need to restart the application to see the changes."
echo "If running with Docker: docker-compose restart"
echo "============================================================"