#!/bin/bash
# GearVue Equipment Tracker Backup Script
# This script creates a backup of the application data

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}GearVue Equipment Tracker - Backup Script${NC}"
echo "============================================================"

# Create backup directory
BACKUP_DIR="backup/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

echo -e "${YELLOW}Creating backup in $BACKUP_DIR...${NC}"

# Determine if the application is running in Docker
if docker ps | grep -q "gearvue-app"; then
    echo "Application is running in Docker, creating volume snapshot..."
    
    # Create a temporary container to access the volume data
    CONTAINER_ID=$(docker create --name gearvue-backup-tmp -v gearvue_data:/data alpine:latest)
    
    # Start the container
    docker start $CONTAINER_ID
    
    # Copy data from container
    echo "Copying data from Docker volume..."
    docker cp $CONTAINER_ID:/data "$BACKUP_DIR/app_data"
    
    # Remove temporary container
    docker rm -f $CONTAINER_ID
    
    # Compress the data
    echo "Compressing data..."
    tar -czf "$BACKUP_DIR/app_data.tar.gz" -C "$BACKUP_DIR" app_data
    rm -rf "$BACKUP_DIR/app_data"
else
    # Check if local data directory exists
    if [ -d "app/data" ]; then
        echo "Creating backup of local data directory..."
        tar -czf "$BACKUP_DIR/app_data.tar.gz" -C app data
    else
        echo -e "${RED}Error: Could not find app/data directory.${NC}"
        echo "Make sure you're running this script from the GearVue root directory."
        exit 1
    fi
fi

# Backup .env file if it exists
if [ -f ".env" ]; then
    echo "Backing up environment configuration..."
    cp .env "$BACKUP_DIR/.env.backup"
fi

# Backup logs if they exist
if [ -d "logs" ]; then
    echo "Backing up logs..."
    tar -czf "$BACKUP_DIR/logs.tar.gz" logs
fi

# Create a symlink to the latest backup
echo "Creating link to latest backup..."
rm -f backup/latest
ln -sf "$BACKUP_DIR" backup/latest

# Create a backup list file
echo "Creating backup inventory..."
echo "GearVue Backup - $(date)" > "$BACKUP_DIR/backup_inventory.txt"
echo "Contents:" >> "$BACKUP_DIR/backup_inventory.txt"
ls -la "$BACKUP_DIR" >> "$BACKUP_DIR/backup_inventory.txt"

echo -e "${GREEN}Backup completed successfully!${NC}"
echo "Backup saved to: $BACKUP_DIR"
echo "Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"
echo "============================================================"
echo "To restore this backup, run: ./restore.sh $BACKUP_DIR"
echo "============================================================"