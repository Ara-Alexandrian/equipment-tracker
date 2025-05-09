# Equipment Tracker Project Summary

This document provides a summary of the equipment tracker application and instructions for running and testing the system.

## Overview

The Equipment Tracker is a web-based application designed for clinical physicists and day-to-day users to manage health physics equipment inventory, track calibration schedules, and monitor equipment location. The system includes:

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
   python run.py
   ```

2. Open your browser and navigate to http://localhost:5000

### Option 2: Using Docker

1. Build and run the Docker container:
   ```bash
   cd /config/github/equipment-tracker
   docker build -t equipment-tracker .
   docker run -p 5000:5000 equipment-tracker
   ```

2. Open your browser and navigate to http://localhost:5000

## Testing the Application

1. **Login with different users**:
   - Administrator: username `admin`, password `admin123`
   - Clinical Physicist: username `physicist`, password `physicist123`
   - Regular User: username `user`, password `user123`

2. **Test the visual dashboard**:
   - Navigate to the Visual Dashboard
   - Try different visualization layouts
   - Filter by equipment category

3. **Test the checkout system**:
   - Find a piece of equipment
   - Click "View" to see details
   - Check out the equipment
   - Return to the checkout dashboard to see status
   - Return the equipment

4. **Test report generation**:
   - Login as admin or physicist
   - Go to Administration > Generate Reports
   - Select different report types
   - Try different formats (PDF, CSV)

## Future Enhancements

1. **Notifications System**:
   - Email alerts for upcoming calibrations
   - Overdue equipment notifications

2. **Advanced Data Import**:
   - Direct database connection options
   - API-based data import

3. **Mobile Application**:
   - Companion mobile app for scanning equipment
   - QR code integration

4. **Advanced Analytics**:
   - Predictive maintenance suggestions
   - Cost analysis for calibration and maintenance

## Project Structure

The application follows a modular design with clear separation of concerns:

- **Models**: Data handling and business logic
- **Routes**: HTTP request handling and API endpoints
- **Templates**: User interface rendering
- **Static Assets**: CSS, JavaScript, and images

This architecture makes it easy to extend the application with new features while maintaining code quality and testability.