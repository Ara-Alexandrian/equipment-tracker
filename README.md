# GearVue - Medical Physics Equipment Management System

<div align="center">
  <img src="Resources/GearVue-Whitebackground.jpg" alt="GearVue Logo" width="400">
  <br>
  <i>Comprehensive equipment tracking for medical physics departments</i>
  <br><br>
</div>

A powerful web-based application for tracking medical physics equipment, managing calibrations, and streamlining workflows through innovative QR code technology.

## Overview

GearVue is designed for clinical physicists and support staff to efficiently manage their equipment inventory, track calibration schedules, and monitor equipment location. The system includes:

### Key Features

- **Equipment Dashboard:** Overview of all equipment with visual status indicators
- **Calibration Tracking:** Monitor calibration due dates and receive email notifications
- **Equipment Checkout System:** Track equipment locations and complete checkout history
- **Zero-Friction QR Code System:** Scan equipment QR codes for instant access - no login required
- **Transport Request System:** Request and track equipment movements between locations
- **Ticketing System:** Submit and track equipment issues with traffic light status indicators
- **Visual Interface:** Interactive network visualization of equipment relationships
- **User Management:** Role-based access control (Admin, Physicist, Regular User)
- **Reporting:** Generate PDF, CSV, and Excel reports for audits and reviews
- **Multiple Themes:** Light, Dark, Dracula, and other visual themes

## Deployment Options

GearVue offers several deployment methods to suit different environments:

### 1. Standard Docker Deployment

```bash
# Clone the repository
git clone https://github.com/yourusername/gearvue.git
cd gearvue

# Run the deployment script
./deploy.sh
```

This interactive script will guide you through configuring and starting the application.

### 2. Organization-Specific Deployments

For specific organizational requirements, we provide pre-configured deployment options:

- **Mary Bird Perkins Cancer Center:**
  ```bash
  ./mbp-deploy.sh  # Configured for 172.30.98.21:7373
  ```

- **A-NaviQ:**
  ```bash
  ./anaviq-deploy.sh  # Configured for 192.168.1.11:8889
  ```

- **Unraid Servers:**
  - Add the Docker template in Unraid's Community Applications
  - Template URL: `https://raw.githubusercontent.com/organization/gearvue/main/unraid/gearvue.xml`

### 3. Manual Setup

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

For detailed deployment instructions, see:
- [Docker Deployment Guide](docs/DOCKER_DEPLOYMENT.md)
- [Mary Bird Perkins Deployment](docs/MBP_DEPLOYMENT.md)
- [A-NaviQ Deployment](docs/ANAVIQ_DEPLOYMENT.md)
- [Unraid Deployment](docs/UNRAID_DEPLOYMENT.md)

## System Architecture

The application follows a modular design with clear separation of concerns:

- **Models**: Data handling and business logic
- **Routes**: HTTP request handling and API endpoints
- **Templates**: User interface rendering
- **Static Assets**: CSS, JavaScript, and images

### Data Management

The application uses JSON files for data storage, located in the `app/data` directory:
- `equipment.json`: Equipment metadata
- `equipment_status.json`: Current status and location of equipment
- `users.json`: User accounts, roles, and notification preferences
- `checkout_history.json`: History of equipment checkout activities
- `notification_logs.json`: History of sent calibration notifications
- `tickets.json`: Equipment issue tickets and comments
- `equipment_conditions.json`: Traffic light status indicators (green/yellow/red)
- `transport_requests.json`: Equipment transport requests and movement tracking
- `auto_reports_config.json`: Automatic report generation settings

## Key Features

### Zero-Friction QR Code System

The application features a zero-friction QR code system that allows users to:

1. Scan QR codes attached to equipment to view details
2. Check equipment in/out without login
3. Submit issue tickets directly from mobile devices
4. Request equipment transport between locations
5. View equipment status with visual traffic light indicators

To use the QR code system:
1. Administrators can generate QR codes from the equipment detail page
2. Print and attach QR codes to physical equipment
3. Users can scan codes with their mobile devices and immediately take action

See [QR_CODE_GUIDE.md](docs/QR_CODE_GUIDE.md) for detailed instructions and best practices.

### Transport Request System

The transport request system allows users to:

1. Request equipment movement between locations
2. Track the status of transport requests
3. Coordinate calibration shipments
4. Manage approvals and schedules

For information on using the transport request system, refer to [TRANSPORT_GUIDE.md](docs/TRANSPORT_GUIDE.md).

### Email Notifications

The application includes an email notification system for calibration alerts. You can configure the email settings using environment variables:

```bash
export MAIL_SERVER=smtp.example.com
export MAIL_PORT=587
export MAIL_USERNAME=your-username
export MAIL_PASSWORD=your-password
export MAIL_USE_TLS=True
export MAIL_DEFAULT_SENDER=gearvue@example.com
```

For Docker deployment, these variables can be set in the docker-compose.yml file or through the deployment scripts.

The included cron job automatically checks for upcoming and overdue calibrations daily at 8:00 AM and sends notifications to users with appropriate roles and preferences.

### Automatic Reports

The system can generate scheduled reports in various formats:

- Daily calibration reports
- Weekly inventory and checkout reports
- Monthly comprehensive reports
- Custom report configurations

Reports can be automatically emailed to designated recipients and stored for future reference.

## User Accounts

Default user accounts for testing:
- Admin: username `admin`, password `admin123`
- Physicist: username `physicist`, password `physicist123`
- Regular User: username `user`, password `user123`

## Theme Support

The application supports multiple themes:
- Light Mode: Standard clean interface
- Dark Mode: Reduced eye strain for low-light environments
- Dracula Mode: High contrast theme with distinct visual identity
- Sweet Dracula Mode: Softer version of Dracula
- Pastel Mode: Light theme with soft pastel colors

Features include:
- Automatic detection of system preferences
- Manual toggle in the navigation bar
- Persistent theme selection using localStorage across sessions
- Custom icons for each theme

## Development Workflow

### Branch Management

**IMPORTANT: Never commit directly to the main branch!**

Always follow these guidelines for development:

1. **Create a new branch for all changes**:
   ```bash
   git checkout main     # Start from the main branch
   git pull              # Ensure you have the latest changes
   git checkout -b feature/your-feature-name  # Create a new branch
   ```

2. **Make changes on your branch**:
   - Implement your changes
   - Test thoroughly
   - Commit regularly with descriptive messages

3. **Merge to main via Pull Request**:
   - Push your branch to remote
   - Create a pull request
   - Get code review
   - Merge only after approval

4. **Delete branches after merging**:
   - Clean up branches that have been merged

This workflow ensures that:
- Main branch always remains stable
- Changes are reviewed before being merged
- We maintain a clean project history
- We avoid conflicts and accidental code loss

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

## Documentation

For complete documentation, see the [Documentation Index](docs/README.md).

## Project Structure

```
gearvue/
├── app/                    # Application code
│   ├── data/               # JSON data files
│   ├── models/             # Data managers
│   ├── routes/             # Route handlers
│   ├── static/             # Static assets (CSS, JS, images)
│   └── templates/          # HTML templates
├── docs/                   # Documentation files
│   ├── README.md           # Documentation index
│   ├── DOCKER_DEPLOYMENT.md # Docker deployment guide
│   ├── MBP_DEPLOYMENT.md   # Mary Bird Perkins guide
│   ├── ANAVIQ_DEPLOYMENT.md # A-NaviQ deployment guide
│   ├── UNRAID_DEPLOYMENT.md # Unraid deployment guide
│   ├── QR_CODE_GUIDE.md    # QR code system guide
│   ├── TRANSPORT_GUIDE.md  # Transport system guide
│   ├── THEME_SYSTEM.md     # Theme system documentation
│   ├── CODE_STANDARDS.md   # Coding standards
│   └── CHANGELOG.md        # Version history
├── docker/                 # Docker configuration
├── unraid/                 # Unraid Docker template
├── logs/                   # Log files
├── scripts/                # Utility scripts
└── tests/                  # Test suite
```

## Running Tests

```bash
python -m unittest tests/test_equipment_tracker.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.