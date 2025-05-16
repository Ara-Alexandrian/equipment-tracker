# Mary Bird Perkins GearVue Deployment Guide

<div align="center">
  <img src="../Resources/Mary Bird Perkins Cancer Center.png" alt="Mary Bird Perkins Logo" width="400">
  <br>
  <i>GearVue Deployment Guide for Mary Bird Perkins Cancer Center</i>
  <br><br>
</div>

## Overview

This guide provides instructions for deploying the GearVue Equipment Tracker specifically configured for Mary Bird Perkins Cancer Center on server 172.30.98.21 port 7373.

## Quick Start

The simplest way to deploy GearVue at Mary Bird Perkins:

1. Log in to the server where you want to deploy GearVue
2. Clone the repository:
   ```bash
   git clone https://github.com/organization/gearvue.git
   cd gearvue
   ```

3. Run the MBP-specific deployment script:
   ```bash
   ./mbp-deploy.sh
   ```

4. Follow the on-screen prompts to complete the setup
5. Access GearVue at http://172.30.98.21:7373

## MBP Configuration Details

The Mary Bird Perkins deployment has been preconfigured with:

- **Server Address**: 172.30.98.21:7373
- **SMTP Server**: smtp.marybird.com
- **Default Email**: gearvue@marybird.com
- **Timezone**: America/Chicago
- **Auto-Update**: Daily from main branch

## Automatic Updates

This deployment includes automatic updates from the main branch:

1. **Daily checks**: The system checks once per day for updates
2. **Self-updating**: When updates are found, they are automatically applied
3. **Manual update**: You can force an update with:
   ```bash
   docker exec mbp-gearvue-app /app/update.sh
   ```

## Backup and Restore

For data safety, perform regular backups:

1. **Create backup**:
   ```bash
   ./backup.sh
   ```

2. **Restore from backup**:
   ```bash
   ./restore.sh backup/latest
   ```

## Server Requirements

The Mary Bird Perkins deployment requires:

- Docker and Docker Compose
- At least 2GB of RAM
- 5GB of available disk space
- Firewall allowing access to port 7373
- Network access to SMTP server

## Customizing the Configuration

If you need to modify the Mary Bird Perkins deployment:

1. Edit the `.env.mbp` file:
   ```bash
   nano .env.mbp
   ```

2. Restart the containers:
   ```bash
   docker-compose -f docker-compose.mbp.yml down
   docker-compose -f docker-compose.mbp.yml --env-file .env.mbp up -d
   ```

## Maintenance Commands

Common tasks for maintaining the GearVue deployment:

### Viewing Logs
```bash
docker-compose -f docker-compose.mbp.yml logs -f
```

### Stopping the Application
```bash
docker-compose -f docker-compose.mbp.yml down
```

### Restarting the Application
```bash
docker-compose -f docker-compose.mbp.yml restart
```

### Checking Container Status
```bash
docker-compose -f docker-compose.mbp.yml ps
```

### Accessing the Application Shell
```bash
docker exec -it mbp-gearvue-app bash
```

## Troubleshooting

If you encounter issues with the Mary Bird Perkins deployment:

1. **Application not accessible**:
   - Verify the server firewall allows traffic on port 7373
   - Check if the IP address is correctly bound to the port:
     ```bash
     netstat -tuln | grep 7373
     ```

2. **Email notifications not sending**:
   - Verify SMTP credentials in `.env.mbp`
   - Check connectivity to smtp.marybird.com from the server

3. **Auto-updates not working**:
   - Verify the server has internet access
   - Check if the container has proper permissions:
     ```bash
     docker exec mbp-gearvue-app git fetch
     ```

For additional assistance, please contact:
- Email: aalexandrian@marybird.com
- Phone: Extension 555

---

<div align="center">
  <p>Developed for Mary Bird Perkins Cancer Center</p>
  <p>Department of Medical Physics</p>
</div>