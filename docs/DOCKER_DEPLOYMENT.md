# GearVue Docker Deployment Guide

<div align="center">
  <img src="../Resources/GearVue-Whitebackground.jpg" alt="GearVue Logo" width="400">
  <br>
  <i>Docker Deployment Guide for Medical Physics Equipment Management System</i>
  <br><br>
</div>

## 🐳 Docker Deployment Options

GearVue has been designed to be easily deployed using Docker, providing a consistent, isolated environment that simplifies setup and maintenance. This guide covers multiple deployment options to fit different environments and requirements.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Start Deployment](#quick-start-deployment)
- [Manual Deployment](#manual-deployment)
- [Environment Configuration](#environment-configuration)
- [Data Persistence](#data-persistence)
- [Backup and Restore](#backup-and-restore)
- [Security Considerations](#security-considerations)
- [Updating the Application](#updating-the-application)
- [Troubleshooting](#troubleshooting)

## System Requirements

For a standard deployment with up to 50 concurrent users:

- **OS**: Any Linux distribution with Docker support
- **CPU**: 2 cores minimum
- **RAM**: 2GB minimum
- **Storage**: 10GB available space
- **Network**: Port 80/443 accessible
- **Software**: Docker 20.10+ and Docker Compose 2.0+

For larger deployments (50+ concurrent users):

- **CPU**: 4 cores recommended
- **RAM**: 4GB recommended
- **Storage**: 20GB+ available space

## Quick Start Deployment

The easiest way to deploy GearVue is using the automated deployment script.

1. Clone the repository:
   ```bash
   git clone https://github.com/organization/gearvue.git
   cd gearvue
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

3. Follow the on-screen prompts to configure your environment.

4. Access GearVue at the URL configured during setup.

## Manual Deployment

If you prefer more control, you can follow these steps for a manual deployment:

1. Clone the repository:
   ```bash
   git clone https://github.com/organization/gearvue.git
   cd gearvue
   ```

2. Create an environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

4. Access GearVue at http://localhost:5000 (or the configured port)

## Environment Configuration

The following environment variables can be configured:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Application port | `5000` |
| `FLASK_ENV` | Environment (production/development) | `production` |
| `APPLICATION_URL` | Public URL of the application | `http://localhost:5000` |
| `MAIL_SERVER` | SMTP server address | `smtp.example.com` |
| `MAIL_PORT` | SMTP server port | `587` |
| `MAIL_USERNAME` | SMTP username | ` ` |
| `MAIL_PASSWORD` | SMTP password | ` ` |
| `MAIL_USE_TLS` | Use TLS for SMTP | `True` |
| `MAIL_DEFAULT_SENDER` | Default sender email | `equipment-tracker@example.com` |
| `TZ` | Timezone | `America/Chicago` |

## Data Persistence

GearVue stores data in the following locations:

- **Application data**: `/app/app/data` inside the container
- **Logs**: `/app/logs` inside the container
- **Output files**: `/app/output` inside the container
- **Resources**: `/app/Resources` inside the container

These locations are mapped to Docker volumes and host folders in the `docker-compose.yml` file to ensure data persistence across container restarts and updates.

## Backup and Restore

GearVue includes scripts for easy backup and restoration of data:

### Backup

To create a backup of all application data:

```bash
./backup.sh
```

This will create a timestamped backup in the `backup/` directory.

### Restore

To restore from a backup:

```bash
./restore.sh backup/2025-05-15
```

If no directory is specified, the most recent backup will be used.

## HTTPS Configuration

To enable HTTPS with Let's Encrypt, uncomment the Traefik section in the `docker-compose.yml` file and follow these steps:

1. Create necessary Traefik configuration:

```bash
mkdir -p traefik/config traefik/certificates
```

2. Create `traefik/traefik.yaml`:

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: your-email@example.com
      storage: /certificates/acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
  file:
    directory: "/etc/traefik/config"
    watch: true

api:
  dashboard: true
  insecure: false
```

3. Create `traefik/config/dashboard.yaml` for the Traefik dashboard (optional):

```yaml
http:
  routers:
    dashboard:
      rule: "Host(`traefik.yourdomain.com`)"
      service: api@internal
      middlewares: 
        - auth
      tls:
        certResolver: letsencrypt

  middlewares:
    auth:
      basicAuth:
        users:
          - "admin:$apr1$ruca84Hq$mbjdMZBAG.KWn7vfN/SNK/" # Change this!
```

4. Add Traefik labels to the `app` service in `docker-compose.yml`:

```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.gearvue.rule=Host(`gearvue.yourdomain.com`)"
  - "traefik.http.routers.gearvue.entrypoints=websecure"
  - "traefik.http.routers.gearvue.tls=true"
  - "traefik.http.routers.gearvue.tls.certresolver=letsencrypt"
  - "traefik.http.services.gearvue.loadbalancer.server.port=5000"
```

5. Update your `.env` file with the proper `APPLICATION_URL`:

```
APPLICATION_URL=https://gearvue.yourdomain.com
```

## Updating the Application

To update to a newer version:

1. Pull the latest code:
   ```bash
   git pull
   ```

2. Rebuild and restart containers:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Troubleshooting

### Common Issues

#### Application not accessible

1. Check if containers are running:
   ```bash
   docker-compose ps
   ```

2. Check container logs:
   ```bash
   docker-compose logs app
   ```

#### Email notifications not being sent

1. Verify SMTP settings in .env file
2. Check cron container logs:
   ```bash
   docker-compose logs cron
   ```

#### Permissions issues

If you encounter permission problems:

```bash
# Fix ownership of mounted volumes
sudo chown -R 1000:1000 app/data logs output Resources
```

### Getting Support

If you need additional help:

- Check the GitHub repository issues section
- Contact support at equipment-tracker@marybird.com

---

<div align="center">
  <p>Developed for Mary Bird Perkins Cancer Center</p>
  <p>Department of Medical Physics</p>
</div>