# Changelog

## Latest Changes

### Transport Request System (Current)

- **Equipment Movement Tracking**: Complete system for requesting and tracking equipment transport between locations
- **QR Code Integration**: Zero-friction transport requests through QR code scanning
- **Status Lifecycle**: Request → Approve → Schedule → In Transit → Complete flow
- **Mobile-Optimized**: Smartphone-friendly interface for on-the-go transport requests
- **Visual Indicators**: Transport badges in equipment lists show movement status
- **Dashboard Integration**: Transport widget shows pending movements on main dashboard
- **Role-Based Permissions**: Physicists and admins can approve and manage requests
- **Documentation**: Comprehensive Transport Guide for users

### Zero-Friction QR Code System

- **Complete Login-Free Access**: Implemented truly frictionless QR code system with no login barriers
- **Dedicated QR Routes**: Created special `/qr` routes that bypass all authentication
- **Mobile-First Design**: Optimized templates for smartphone users scanning QR codes
- **Instant Actions**: Users can check out equipment, request transport, and submit tickets immediately
- **User Identification**: Simple name/initials entry or dropdown selection
- **Traffic Light System**: Visual indicators (green/yellow/red) for equipment status
- **Enhanced Documentation**: Comprehensive QR code guide and updated README

### Ticket System Implementation

- **Equipment Issue Tracking**: Created ticketing system for equipment issues/maintenance
- **Condition Indicators**: Implemented traffic light system (normal/warning/critical)
- **Equipment QR Codes**: Generate and print QR codes for equipment
- **User Information Display**: Enhanced visibility of who is checking out equipment

### Core Features

- **Equipment Dashboard**: Overview of all equipment with status indicators
- **Calibration Tracking**: Monitor calibration due dates with email notifications
- **Equipment Checkout System**: Track equipment locations and checkout history
- **Visual Interface**: Interactive network visualization of equipment relationships
- **User Management**: Role-based access control (Admin, Physicist, Regular User)
- **Reporting**: Generate PDF, CSV, and Excel reports for audits and reviews

## Technical Improvements

### Authentication & Security

- **QR-Specific Routes**: Dedicated routes that bypass login requirements
- **CSRF Protection**: Disabled for mobile users to ensure frictionless access
- **Session Handling**: Special headers to override authentication checks

### Mobile Optimization

- **Touch-Friendly UI**: Large buttons and simplified forms for mobile devices
- **Responsive Design**: Adapts to different screen sizes with Bootstrap
- **Streamlined Forms**: Minimal fields required for quick actions

### Code Structure

- **Modular Design**: Separate blueprints for different system components
- **JSON Data Storage**: Structured data files for equipment, tickets, users, etc.
- **Clean Architecture**: Separation of models, routes, and templates