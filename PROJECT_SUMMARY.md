# Medical Physics Equipment Tracker Project Summary

This document provides a summary of the equipment tracker application and instructions for running and testing the system.

## Overview

The Equipment Tracker is a web-based application designed for clinical physicists and day-to-day users to manage medical physics equipment inventory, track calibration schedules, and monitor equipment location. The system includes:

1. **Equipment Management Dashboard**
   - View and search all equipment
   - Track calibration status
   - Filter by equipment type and location

2. **Visual Status Dashboard**
   - Interactive network visualization
   - Real-time status updates
   - Visual charts and graphs

3. **Equipment Checkout System**
   - Check out equipment to temporary locations
   - Track equipment status
   - Monitor checkout history

4. **Administrative Tools**
   - Role-based access control
   - User management
   - Report generation

## Key Features Implemented

- **Unified Data Model**: Combined data from multiple Excel sheets into a single coherent model
- **Interactive Visualizations**: D3.js-based network visualization of equipment relationships
- **Checkout System**: Complete system for tracking equipment location and status
- **Report Generation**: PDF, Excel, and CSV report generation for audits
- **Role-Based Access**: Three user roles with appropriate permissions
- **Containerized Deployment**: Docker support for easy deployment

## Running the Application

### Option 1: Using Python Directly

1. Run the application:
   ```bash
   cd /config/github/equipment-tracker
   
   # Using the start script (recommended):
   ./start.sh
   
   # Or manually:
   # For local access only:
   python run.py
   
   # For external network access:
   python run.py --host 0.0.0.0 --port 5000
   ```

2. Open your browser and navigate to:
   - Local access: http://localhost:5000
   - External access: http://YOUR_IP_ADDRESS:5000 (e.g., http://192.168.1.11:5000)

### Option 2: Using Docker

1. Build and run the Docker container:
   ```bash
   cd /config/github/equipment-tracker
   
   # Build the image
   docker build -t equipment-tracker .
   
   # Run the container
   docker run -p 5000:5000 -e APPLICATION_URL=http://YOUR_IP_ADDRESS:5000 equipment-tracker
   
   # Or use docker-compose (recommended)
   export APPLICATION_URL=http://YOUR_IP_ADDRESS:5000  # Replace with your IP
   docker-compose up -d
   ```

2. Open your browser and navigate to:
   - Local access: http://localhost:5000
   - External access: http://YOUR_IP_ADDRESS:5000 (e.g., http://192.168.1.11:5000)

## Testing the Application

1. **Test the QR code system** (main way users will interact):
   - Scan a QR code for equipment (admins can generate these)
   - Check out equipment without login
   - Submit an issue ticket without login
   - Check in equipment without login
   - View the traffic light status indicators

2. **Login with different users** (for administrative functions):
   - Administrator: username `admin`, password `admin123`
   - Clinical Physicist: username `physicist`, password `physicist123`
   - Regular User: username `user`, password `user123`

3. **Test the ticket system**:
   - Create a ticket for equipment
   - View ticket details and add comments
   - Change equipment condition (admin/physicist only)
   - View equipment with different conditions

4. **Test the visual dashboard**:
   - Navigate to the Visual Dashboard
   - Try different visualization layouts
   - Filter by equipment category

5. **Test the checkout system**:
   - Find a piece of equipment
   - Click "View" to see details
   - Check out the equipment
   - Return to the checkout dashboard to see status
   - Return the equipment

6. **Test report generation**:
   - Login as admin or physicist
   - Go to Administration > Generate Reports
   - Select different report types
   - Try different formats (PDF, CSV)

## Recent Enhancements

1. **Zero-Friction QR Code System**:
   - Scan equipment QR codes for instant access with no login
   - Mobile-optimized interface for smartphones
   - Check out equipment and submit issues directly from QR scan
   - Visual traffic light system (green/yellow/red) for equipment status

2. **Equipment Ticket System**:
   - Create and track equipment issues and maintenance requests
   - Visual condition indicators (normal/warning/critical)
   - Role-based permissions for condition changes
   - Complete comment and history tracking

3. **Enhanced User Information**:
   - Clear visibility of who has checked out equipment
   - Full user names displayed throughout the system
   - Ticket and checkout history with user details
   - Simplified user selection for mobile users

4. **Dark Mode Support**:
   - Toggle between light and dark themes
   - Persistent theme selection using localStorage
   - Improved UI with appropriate color schemes for both modes

5. **Notifications System**:
   - Email alerts for upcoming calibrations
   - Overdue equipment notifications
   - User-configurable notification preferences
   - Notification history tracking

6. **Administrative Interface**:
   - Equipment management with CRUD operations
   - User management with role assignment
   - Advanced report generation options
   - Calibration tracking and alerts

## Future Enhancements

1. **Advanced Data Import**:
   - Direct database connection options
   - API-based data import

2. **QR Code System** ✅ IMPLEMENTED:
   - Zero-friction equipment interaction without login
   - Mobile-optimized interface for QR code scanning
   - Traffic light system for equipment status tracking

3. **Advanced Analytics**:
   - Predictive maintenance suggestions
   - Cost analysis for calibration and maintenance

## Project Structure

The application follows a modular design with clear separation of concerns:

- **Models**: Data handling and business logic
- **Routes**: HTTP request handling and API endpoints
- **Templates**: User interface rendering
- **Static Assets**: CSS, JavaScript, and images

This architecture makes it easy to extend the application with new features while maintaining code quality and testability.