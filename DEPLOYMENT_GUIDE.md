# GearVue Deployment Guide

<div align="center">
  <img src="Resources/gearvue-text.png" alt="GearVue Logo" width="400">
  <br>
  <i>Medical Physics Equipment Management System</i>
  <br><br>
</div>

## 📋 System Overview

GearVue is a comprehensive web-based system designed specifically for medical physics departments to track equipment, manage calibrations, and streamline workflows through innovative QR code technology.

| Feature | Description |
|---------|-------------|
| **Equipment Tracking** | Complete inventory management with status indicators |
| **Calibration Management** | Automated tracking and notifications for calibration due dates |
| **Location Tracking** | Real-time equipment location and checkout history |
| **Transport Management** | Request and track equipment movements between locations |
| **QR Code System** | Zero-friction mobile access with no login requirements |
| **Ticketing System** | Issue reporting with severity levels and status tracking |
| **Theme Support** | Light, Dark, and Dracula modes with persistent preferences |

## 🔧 Technical Requirements

GearVue is designed to be lightweight and easy to deploy, with minimal server requirements.

### Base Requirements

- **Server**: Any standard web server (Apache/Nginx)
- **Runtime**: Python 3.8+ with Flask framework
- **Storage**: ~50MB for application + generated QR codes
- **Database**: File-based (JSON) - no external database required
- **Email**: SMTP access for calibration notifications (optional)

### Technology Stack

```
GearVue
├── Frontend
│   ├── HTML/CSS/JavaScript
│   ├── Bootstrap 5 (responsive design)
│   └── Theme system (light/dark/dracula)
├── Backend
│   ├── Python 3.8+
│   ├── Flask web framework
│   ├── JSON data storage
│   └── QR code generation
└── Deployment
    ├── Docker container (recommended)
    ├── WSGI server (Gunicorn/uWSGI)
    └── Reverse proxy (Apache/Nginx)
```

## 🔐 Security Considerations

GearVue was designed with simplicity and security in mind:

- **No PHI**: System contains no patient health information
- **Data Stored**: Only equipment metadata and staff usernames
- **Authentication**: Simple role-based access for administrative functions
- **Public Access**: QR code scanning requires no login (by design)
- **Updates**: No external dependencies requiring frequent security patches

## 🚀 Deployment Options

### 1. Docker Container (Recommended)

<details>
<summary>Expand for details</summary>

```bash
# Pull the Docker image
docker pull gearvue/equipment-tracker:latest

# Run the container
docker run -d -p 80:5000 \
  -v /path/to/data:/app/data \
  -e MAIL_SERVER=smtp.example.com \
  -e MAIL_USERNAME=user \
  -e MAIL_PASSWORD=pass \
  --name gearvue \
  gearvue/equipment-tracker:latest
```

**Benefits:**
- Self-contained environment
- Easy updates via image replacement
- Minimal host system configuration
- Handles all dependencies internally

</details>

### 2. Standard Web Hosting

<details>
<summary>Expand for details</summary>

```bash
# Clone the repository
git clone https://github.com/organization/gearvue.git
cd gearvue

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Gunicorn
gunicorn --workers=3 --bind=127.0.0.1:5000 run:app
```

Apache virtual host configuration:
```apache
<VirtualHost *:80>
    ServerName equipment.example.com
    
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    ErrorLog ${APACHE_LOG_DIR}/equipment_error.log
    CustomLog ${APACHE_LOG_DIR}/equipment_access.log combined
</VirtualHost>
```

**Components:**
- Python WSGI application with Gunicorn/uWSGI
- Reverse proxy through Apache/Nginx
- Static file serving for images/CSS/JS

</details>

### 3. Cloud Deployment

<details>
<summary>Expand for details</summary>

#### Azure App Service

```bash
# Login to Azure
az login

# Create resource group
az group create --name gearvue-rg --location eastus

# Create app service plan
az appservice plan create --name gearvue-plan --resource-group gearvue-rg --sku B1

# Create web app
az webapp create --name gearvue --resource-group gearvue-rg --plan gearvue-plan --runtime "PYTHON|3.8"

# Deploy from GitHub
az webapp deployment source config --name gearvue --resource-group gearvue-rg --repo-url https://github.com/yourusername/gearvue --branch main
```

**Other Cloud Options:**

- **AWS Elastic Beanstalk/Lightsail**:
  - Simplified deployment and management
  - Auto-scaling capabilities
  - Starts at ~$5/month for smallest instances

- **Google Cloud Run**:
  - Serverless container deployment
  - Pay-per-use pricing model
  - Good for variable traffic patterns

- **Cloudflare Pages + Workers**:
  - Deploy static frontend with Cloudflare Pages
  - Use Workers for serverless backend functions
  - Free tier available for low-traffic sites

</details>

## 🌐 Public Deployment Requirements

When deploying GearVue to a public-facing environment:

| Requirement | Description |
|-------------|-------------|
| **Domain Name** | Required for public access (e.g., `equipment.marybird.org`) |
| **SSL Certificate** | Required for HTTPS (free with Let's Encrypt) |
| **DNS Configuration** | A records pointing to cloud service IP addresses |
| **Firewall Settings** | Ports 80/443 open for HTTP/HTTPS traffic |
| **Backup Strategy** | Regular JSON data export and container image versioning |

## 💻 Resource Requirements

GearVue is designed to run efficiently with minimal resources:

- **Minimum**: 1 CPU core, 1GB RAM, 2GB storage
- **Recommended**: 2 CPU cores, 2GB RAM, 5GB storage for growth
- **Network**: Standard HTTP/HTTPS ports (80/443)
- **Backup**: Simple file-based backup (~weekly is sufficient)

## 🔍 Technology Glossary

For IT professionals who may be new to some of these technologies:

- **Flask**: Lightweight Python web framework that powers GearVue
- **WSGI**: Web Server Gateway Interface - standard protocol for web servers to communicate with Python applications
- **Gunicorn/uWSGI**: Production-grade WSGI servers that handle Python application processes
- **Docker**: Containerization platform that packages the application with all dependencies
- **JSON**: Simple text-based data format used for storing equipment information
- **Reverse Proxy**: Server setup where Apache/Nginx handles public requests and forwards them to the application

## 🛠️ IT Support Requirements

GearVue was designed to minimize ongoing IT support needs:

- **Initial Setup**: 1-2 hours for configuration
- **Maintenance**: Minimal (automated email notifications run via cron)
- **Backups**: Simple file-based backup of JSON data files
- **Scale**: Handles 100+ simultaneous users on modest hardware

## 💼 Benefits to Department

- ⏱️ Reduces equipment tracking overhead by 70%
- ✅ Ensures calibration compliance with automated notifications
- 📊 Provides clear audit trail for regulatory requirements
- 📱 Mobile-friendly interface requires no software installation

---

<div align="center">
  <p>Developed for Mary Bird Perkins Cancer Center</p>
  <p>Department of Medical Physics</p>
</div>