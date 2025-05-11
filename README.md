# GearVue - Medical Physics Equipment Management System

A comprehensive web-based application for tracking medical physics equipment, their calibration status, location, and checkout history.

## Features

- **Equipment Dashboard:** Overview of all equipment with status indicators
- **Calibration Tracking:** Monitor calibration due dates and receive email notifications for upcoming and overdue calibrations
- **Equipment Checkout System:** Track equipment locations and checkout history
- **Zero-Friction QR Code System:** Scan equipment QR codes for instant access - no login required
- **Ticketing System:** Submit and track equipment issues with status indicators (green/yellow/red)
- **Visual Interface:** Interactive network visualization of equipment relationships
- **User Management:** Role-based access control (Admin, Physicist, Regular User)
- **Reporting:** Generate PDF, CSV, and Excel reports for audits and reviews

## Setup Instructions

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gearvue.git
   cd gearvue
   ```

2. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

3. Access the application at [http://localhost:5000](http://localhost:5000)

### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gearvue.git
   cd gearvue
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   # Using the start script (recommended):
   ./start.sh
   
   # Or manually:
   # For local access only:
   python run.py
   
   # For external network access:
   python run.py --host 0.0.0.0 --port 5000
   ```

5. Access the application:
   - Local access: [http://localhost:5000](http://localhost:5000)
   - External access: http://YOUR_IP_ADDRESS:5000 (e.g., http://192.168.1.11:5000)

## Configuration

The application uses JSON files for data storage, located in the `app/data` directory:
- `equipment.json`: Equipment metadata
- `equipment_status.json`: Current status and location of equipment
- `users.json`: User accounts, roles, and notification preferences
- `checkout_history.json`: History of equipment checkout activities
- `notification_logs.json`: History of sent calibration notifications
- `tickets.json`: Equipment issue tickets and comments
- `equipment_conditions.json`: Traffic light status indicators (green/yellow/red)

### QR Code System

The application features a zero-friction QR code system that allows users to:

1. Scan QR codes attached to equipment to view details
2. Check equipment in/out without login
3. Submit issue tickets directly from mobile devices
4. View equipment status with visual traffic light indicators

To use the QR code system:
1. Administrators can generate QR codes from the equipment detail page
2. Print and attach QR codes to physical equipment
3. Users can scan codes with their mobile devices and immediately take action

See [QR_CODE_GUIDE.md](QR_CODE_GUIDE.md) for detailed instructions and best practices.

### Email Notifications

The application includes an email notification system for calibration alerts. You can configure the email settings using environment variables:

```bash
export MAIL_SERVER=smtp.marybird.com
export MAIL_PORT=587
export MAIL_USERNAME=your-username
export MAIL_PASSWORD=your-password
export MAIL_USE_TLS=True
export MAIL_DEFAULT_SENDER=gearvue@marybird.com
```

For Docker deployment, these variables can be set in the docker-compose.yml file.

The included cron job automatically checks for upcoming and overdue calibrations daily at 8:00 AM and sends notifications to users with appropriate roles and preferences.

## User Accounts

Default user accounts for testing:
- Admin: username `admin`, password `admin123`
- Physicist: username `physicist`, password `physicist123`
- Regular User: username `user`, password `user123`

### Theme Support

The application supports multiple themes:
- Light Mode: Standard clean interface
- Dark Mode: Reduced eye strain for low-light environments
- Dracula Mode: High contrast theme with distinct visual identity
- Automatic detection of system preferences
- Manual toggle in the navigation bar
- Persistent theme selection using localStorage across sessions

## Development

### Project Structure

```
gearvue/
├── app/                    # Application code
│   ├── data/               # JSON data files
│   ├── models/             # Data managers
│   ├── routes/             # Route handlers
│   ├── static/             # Static assets (CSS, JS, images)
│   └── templates/          # HTML templates
├── scripts/                # Utility scripts
└── docker-compose.yml      # Docker configuration
```

### Running Tests

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.