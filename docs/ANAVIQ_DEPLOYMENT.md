# A-NaviQ GearVue Deployment Guide

<div align="center">
  <img src="../Resources/GearVue-Whitebackground.jpg" alt="GearVue Logo" width="400">
  <br>
  <i>GearVue Deployment Guide for A-NaviQ at 192.168.1.11:8889</i>
  <br><br>
</div>

## Overview

This guide provides instructions for deploying the GearVue Equipment Tracker specifically configured for A-NaviQ on server 192.168.1.11 port 8889.

## Quick Start

The simplest way to deploy GearVue at A-NaviQ:

1. Log in to the server as a user with Docker privileges
2. Clone the repository:
   ```bash
   git clone https://github.com/organization/gearvue.git
   cd gearvue
   ```

3. Run the A-NaviQ-specific deployment script:
   ```bash
   ./anaviq-deploy.sh
   ```

4. Follow the on-screen prompts to complete the setup
5. Access GearVue at http://192.168.1.11:8889

## A-NaviQ Configuration Details

The A-NaviQ deployment has been preconfigured with:

- **Server Address**: 192.168.1.11:8889
- **SMTP Server**: smtp.a-naviq.com
- **Default Email**: gearvue@a-naviq.com
- **Timezone**: America/New_York
- **Auto-Update**: Daily from main branch at 4 AM

## Automatic Updates

This deployment includes two layers of automatic updates:

1. **Internal Git-based updates**: 
   - Daily check at 4 AM for updates to the main branch
   - Automatically pulls and applies changes
   - Updates dependencies as needed

2. **Container-level updates**:
   - Watchtower monitors for container changes
   - Rebuilds containers daily if needed
   - Maintains consistency of the entire deployment

You can trigger a manual update at any time with:
```bash
docker exec anaviq-gearvue-app /app/update.sh
```

## Backup and Restore

The A-NaviQ deployment includes backup capabilities:

1. **Create backup**:
   ```bash
   # Inside the gearvue directory
   ./backup.sh
   ```

2. **Restore from backup**:
   ```bash
   ./restore.sh backup/latest
   ```

Backups are stored in the `backup/` directory with timestamped folders.

## Server Requirements

The A-NaviQ deployment requires:

- Docker and Docker Compose
- At least 2GB of RAM
- 5GB of available disk space
- Network access to port 8889 on 192.168.1.11
- Network access to SMTP server

## Customizing the Configuration

If you need to modify the A-NaviQ deployment:

1. Edit the `.env.anaviq` file:
   ```bash
   nano .env.anaviq
   ```

2. Restart the containers:
   ```bash
   docker-compose -f docker-compose.anaviq.yml down
   docker-compose -f docker-compose.anaviq.yml --env-file .env.anaviq up -d
   ```

## Maintenance Commands

Common tasks for maintaining the GearVue deployment:

### Viewing Logs
```bash
docker-compose -f docker-compose.anaviq.yml logs -f
```

### Stopping the Application
```bash
docker-compose -f docker-compose.anaviq.yml down
```

### Restarting the Application
```bash
docker-compose -f docker-compose.anaviq.yml restart
```

### Checking Container Status
```bash
docker-compose -f docker-compose.anaviq.yml ps
```

### Manually Updating to Latest Version
```bash
docker exec anaviq-gearvue-app /app/update.sh
```

### Backing Up Data
```bash
./backup.sh
```

## Troubleshooting

Common issues and solutions:

### Application Not Starting
If the application doesn't start properly:
```bash
# Check container logs
docker-compose -f docker-compose.anaviq.yml logs app

# Verify port availability
sudo netstat -tuln | grep 8889

# Check Docker service status
sudo systemctl status docker
```

### Updates Not Working
If automatic updates aren't applying:
```bash
# Check update logs
docker exec anaviq-gearvue-app cat /app/logs/update.log

# Verify Git access
docker exec anaviq-gearvue-app git remote -v

# Run update manually
docker exec anaviq-gearvue-app /app/update.sh
```

### Email Notifications Not Sending
If email notifications aren't working:
```bash
# Check mail configuration
docker exec anaviq-gearvue-app env | grep MAIL

# Verify SMTP connectivity
docker exec anaviq-gearvue-app ping -c 3 smtp.a-naviq.com

# Check cron logs
docker exec anaviq-gearvue-cron cat /var/log/cron.log
```

## Monitoring and Health Checks

The A-NaviQ deployment includes health checks:

- Every 30 seconds, the application is checked for responsiveness
- Automatic restart if the health check fails 3 times
- Container status visible in Docker Compose output

---

<div align="center">
  <p>A-NaviQ GearVue Equipment Tracker Deployment</p>
  <p>For support contact: support@a-naviq.com</p>
</div>