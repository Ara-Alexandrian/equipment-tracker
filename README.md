# Health Physics Equipment Tracker

A comprehensive web-based application for tracking health physics equipment, their calibration status, location, and checkout history.

## Features

- **Equipment Dashboard:** Overview of all equipment with status indicators
- **Calibration Tracking:** Monitor calibration due dates and get alerts for upcoming calibrations
- **Equipment Checkout System:** Track equipment locations and checkout history
- **Visual Interface:** Interactive network visualization of equipment relationships
- **User Management:** Role-based access control (Admin, Physicist, Regular User)
- **Reporting:** Generate PDF, CSV, and Excel reports for audits and reviews

## Setup Instructions

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/equipment-tracker.git
   cd equipment-tracker
   ```

2. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

3. Access the application at [http://localhost:5000](http://localhost:5000)

### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/equipment-tracker.git
   cd equipment-tracker
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
   python run.py
   ```

5. Access the application at [http://localhost:5000](http://localhost:5000)

## Configuration

The application uses JSON files for data storage, located in the `app/data` directory:
- `equipment.json`: Equipment metadata
- `equipment_status.json`: Current status and location of equipment
- `users.json`: User accounts and roles
- `checkout_history.json`: History of equipment checkout activities

## User Accounts

Default user accounts for testing:
- Admin: username `admin`, password `admin123`
- Physicist: username `physicist`, password `physicist123`
- Regular User: username `user`, password `user123`

## Development

### Project Structure

```
equipment-tracker/
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