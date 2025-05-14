#!/bin/bash
# Cleanup script for GearVue Equipment Tracker
# Created: May 12, 2025
# Updated: May 12, 2025 - Project reorganization

echo "Starting cleanup of GearVue project..."

# Remove Python cache files
echo "Removing Python cache files..."
find /config/github/equipment-tracker -name "__pycache__" -type d -exec rm -rf {} +
find /config/github/equipment-tracker -name "*.pyc" -type f -delete

# Remove backup and duplicated directories
echo "Removing backup directories..."
rm -rf /config/github/equipment-tracker/qrcodes_backup/
rm -rf /config/github/equipment-tracker/archive/resources_backup/
rm -rf /config/github/equipment-tracker/temp_logos/

# Remove template backup files
echo "Removing template backup files..."
rm -f /config/github/equipment-tracker/app/templates/admin/equipment_management.html.bak
rm -f /config/github/equipment-tracker/app/templates/admin/equipment_management_fixed.js
rm -f /config/github/equipment-tracker/app/templates/admin/equipment_management_fixed_modal.js
rm -f /config/github/equipment-tracker/app/templates/admin/equipment_management_fixed.html
rm -f /config/github/equipment-tracker/app/templates/admin/equipment_management_new.html
rm -f /config/github/equipment-tracker/app/templates/admin/calendar_test.html
rm -f /config/github/equipment-tracker/app/templates/admin/direct_form_test.html

# Remove test QR codes
echo "Removing test QR codes..."
rm -f /config/github/equipment-tracker/app/static/qrcodes/test_*.png
rm -f /config/github/equipment-tracker/app/static/qrcodes/temp_url_*.txt

# Clean up error logs
echo "Cleaning up log files..."
> /config/github/equipment-tracker/error_log.txt

# Note: The following files have been reorganized:
# - Test files moved to tests/unit_tests/ directory
# - Debug tools moved to tests/debug_tools/ directory
# - Analysis scripts moved to scripts/analysis/ directory
# - Utility scripts moved to scripts/utilities/ directory

echo "Cleanup completed!"