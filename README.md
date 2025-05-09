# Health Physics Equipment Dashboard

A web-based application for tracking and managing health physics equipment inventory, calibration schedules, and maintenance records. Designed specifically for clinical physicists to track equipment calibration status and for day-to-day users to check out equipment temporarily.

![Equipment Dashboard](app/static/img/dashboard.png)

## Features

- **Interactive Visual Dashboard**: Graphical network visualization of equipment relationships and status
- **Equipment Checkout System**: Track equipment location and status with complete checkout history
- **Calibration Tracking**: Monitor calibration schedules, upcoming due dates, and overdue equipment
- **Administrative Controls**: Role-based access controls for different user types
- **PDF Report Generation**: Create comprehensive reports for audits and external reviews
- **RESTful API**: Programmatic access to equipment data
- **Containerized Deployment**: Docker support for easy deployment

## System Requirements

- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- Excel files with equipment data

## Installation and Setup

### Option 1: Local Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/equipment-tracker.git
   cd equipment-tracker
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Place your Excel files in the Resources directory:
   - `2025 Health Physics Equipment List_Chambers & Electrometers.xls`
   - `2025 Survey Meter Inventory & Calibration_updated 0425.xls`

5. Run the application:
   ```
   python run.py
   ```

6. Open your browser and navigate to http://localhost:5000

### Option 2: Docker Deployment (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/your-username/equipment-tracker.git
   cd equipment-tracker
   ```

2. Place your Excel files in the Resources directory:
   - `2025 Health Physics Equipment List_Chambers & Electrometers.xls`
   - `2025 Survey Meter Inventory & Calibration_updated 0425.xls`

3. Build and start the Docker container:
   ```
   docker-compose up -d
   ```

4. Open your browser and navigate to http://localhost:5000

## User Roles and Permissions

The system has three user roles:

1. **Regular User**
   - Can view equipment details
   - Can check out and return equipment
   - Can view checkout history

2. **Clinical Physicist**
   - All regular user permissions
   - Access to calibration management
   - Can generate reports
   - Can update equipment status

3. **Administrator**
   - All physicist permissions
   - Can manage users
   - Full system configuration access

## Usage Guide

### Dashboard

The main dashboard provides an overview of your equipment inventory with key metrics:
- Total equipment count
- Distribution by category (Chambers, Electrometers, and Survey Meters)
- Recent equipment list

### Visual Dashboard

The interactive visual dashboard provides:
- Network visualization of equipment relationships
- Real-time status updates shown with color-coding
- Multiple visualization layouts (force-directed, radial, tree)
- Interactive charts for status and category distribution

### Equipment Checkout

The checkout system allows you to:
- Track current location of all equipment
- Check out equipment to temporary locations
- Set expected return dates
- View checkout history
- Monitor overdue equipment

### Equipment Details

Click on any equipment entry to view detailed information including:
- Full equipment specifications
- Calibration status and due dates
- Current location and status
- Complete checkout history

### Calibration Tracking

The calibration page provides:
- A list of equipment with upcoming or overdue calibrations
- Visual indicators for calibration status
- Charts showing calibration schedules and distribution

### Report Generation

Administrators and clinical physicists can generate:
- Complete inventory reports
- Calibration status reports
- Checkout status reports
- Maintenance history reports
- Custom date range reports
- PDF, Excel, or CSV formats

## API Reference

The application provides a RESTful API for programmatic access to equipment data:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/equipment` | GET | Get all equipment or filter by category, location, or search query |
| `/api/equipment/<id>` | GET | Get a specific piece of equipment by ID |
| `/api/stats` | GET | Get equipment statistics |
| `/api/locations` | GET | Get unique equipment locations |
| `/api/manufacturers` | GET | Get unique equipment manufacturers |
| `/api/calibration/due-soon` | GET | Get equipment with calibration due soon |
| `/checkout/api/status/<id>` | GET | Get current status and location of equipment |
| `/checkout/api/checkout/<id>` | POST | Check out equipment |
| `/checkout/api/return/<id>` | POST | Return equipment |
| `/visual/api/equipment` | GET | Get equipment data for visualization |
| `/visual/api/equipment/status` | GET | Get equipment status counts |
| `/visual/api/calibration/schedule` | GET | Get calibration schedule data |

## Data Models

### Equipment Data Model

The application uses a unified data model for all equipment types, with these key fields:
- `id`: Unique identifier for each piece of equipment
- `category`: Equipment category (Chamber, Electrometer, Survey Meter)
- `equipment_type`: Specific type within the category
- `manufacturer`: Equipment manufacturer
- `model`: Model name or number
- `serial_number`: Serial number
- `location`: Current location of the equipment
- `calibration_due_date`: When calibration is next due
- `notes`: Additional information

### Checkout System Model

The checkout system tracks:
- Current equipment status (`In Storage`, `Checked Out`, `In Calibration`, `Under Repair`, `Out of Service`)
- Current location
- Checkout history
- User who checked out the equipment
- Expected return date
- Checkout and return timestamps

## Development

### Project Structure

```
equipment-tracker/
├── app/                    # Flask application
│   ├── models/             # Data models
│   │   ├── equipment.py    # Equipment data model
│   │   └── checkout.py     # Checkout system model
│   ├── routes/             # Route handlers
│   │   ├── api.py          # API endpoints
│   │   ├── checkout.py     # Checkout system routes
│   │   ├── dashboard.py    # Main dashboard routes
│   │   ├── reports.py      # Report generation routes
│   │   └── visual.py       # Visual dashboard routes
│   ├── static/             # Static files (CSS, JS, images)
│   └── templates/          # HTML templates
│       ├── checkout/       # Checkout system templates
│       ├── dashboard/      # Dashboard templates
│       ├── reports/        # Report templates
│       └── visual/         # Visual dashboard templates
├── Resources/              # Source Excel files
├── output/                 # Generated output files
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker compose configuration
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

### Default User Accounts

For testing purposes, the system comes with these default user accounts:

1. **Administrator**
   - Username: `admin`
   - Password: `admin123`

2. **Clinical Physicist**
   - Username: `physicist`
   - Password: `physicist123`

3. **Regular User**
   - Username: `user`
   - Password: `user123`

### Extending the Application

To add additional functionality:
1. Update the `requirements.txt` file with new dependencies
2. Add new models in the `app/models/` directory
3. Add new routes in the `app/routes/` directory
4. Create new templates in the `app/templates/` directory
5. Add new API endpoints as needed

## Original Command-line Tools

The original command-line tools are still available for data analysis:

```
python equipment_tracker.py --report [all|summary|calibration|schedule]
python maintenance_tracker.py
python data_explorer.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.