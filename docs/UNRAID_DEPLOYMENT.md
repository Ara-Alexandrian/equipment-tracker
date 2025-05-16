# GearVue Deployment Guide for Unraid

<div align="center">
  <img src="../Resources/GearVue-Whitebackground.jpg" alt="GearVue Logo" width="400">
  <br>
  <i>Deploying GearVue on Unraid OS</i>
  <br><br>
</div>

## Overview

This guide provides step-by-step instructions for deploying GearVue Equipment Tracker on Unraid OS. Unraid's Docker implementation makes it easy to deploy and maintain the application with a user-friendly interface.

## Prerequisites

- Unraid OS version 6.9.0 or later
- Docker already enabled in Unraid
- Community Applications (CA) plugin installed
- Basic understanding of Unraid's web interface

## Deployment Methods

There are two main ways to deploy GearVue on Unraid:

1. **Docker Template** (Recommended): Easy setup through the Unraid web UI
2. **Docker Compose**: More control, but requires command line access

## Method 1: Using Docker Template (Recommended)

### Step 1: Add the Docker Template

1. In your Unraid web interface, navigate to the **Docker** tab
2. Click **Add Container** button in the upper right
3. In the *Template URL* field, enter:
   ```
   https://raw.githubusercontent.com/organization/gearvue/main/unraid/gearvue.xml
   ```
4. Click **Apply**

### Step 2: Configure the Container

After applying the template, you'll see a form to configure the GearVue container:

1. **Name and Repository**
   - These should be pre-filled correctly

2. **Network Type**
   - Select **Bridge** mode

3. **Port Mapping**
   - The Web UI port should be set to `8889` (can be changed if needed)

4. **Path Mappings**
   - **Config**: `/mnt/user/appdata/gearvue/data:/app/app/data`
   - **Logs**: `/mnt/user/appdata/gearvue/logs:/app/logs`
   - **Output**: `/mnt/user/appdata/gearvue/output:/app/output`
   - **Resources**: `/mnt/user/appdata/gearvue/resources:/app/Resources`

5. **Environment Variables** (edit as needed)
   - `MAIL_SERVER`: Your SMTP server address
   - `MAIL_PORT`: SMTP port (usually 587)
   - `MAIL_USERNAME`: Your SMTP username
   - `MAIL_PASSWORD`: Your SMTP password
   - `MAIL_USE_TLS`: True (or False if your server doesn't use TLS)
   - `MAIL_DEFAULT_SENDER`: The email address for notifications
   - `TZ`: Your timezone (e.g., America/Chicago)
   - `APPLICATION_URL`: `http://your-unraid-ip:8889`

6. Click **Apply** to create the container

### Step 3: Access GearVue

1. The container will download and start automatically
2. Once running, navigate to `http://your-unraid-ip:8889` in your browser
3. You should see the GearVue login page

## Method 2: Using Docker Compose (Advanced)

For users comfortable with SSH and the command line, you can use our pre-configured Docker Compose file.

### Step 1: Connect to Unraid via SSH

1. Enable SSH in Unraid (Settings > Management Access)
2. Connect via SSH using your preferred client:
   ```bash
   ssh root@your-unraid-ip
   ```

### Step 2: Install Docker Compose

If not already installed:

```bash
# Create a location for the binary
mkdir -p /usr/local/bin

# Download the latest version
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Step 3: Create the Deployment Directory

```bash
# Create a directory for the application
mkdir -p /mnt/user/appdata/gearvue
cd /mnt/user/appdata/gearvue

# Download the repository or just the docker-compose file
wget https://raw.githubusercontent.com/organization/gearvue/main/docker-compose.unraid.yml -O docker-compose.yml
```

### Step 4: Create .env File

```bash
# Create and edit the environment file
cat > .env << EOL
# GearVue Configuration
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-username
MAIL_PASSWORD=your-password
MAIL_USE_TLS=True
MAIL_DEFAULT_SENDER=gearvue@example.com
TZ=America/Chicago
APPLICATION_URL=http://your-unraid-ip:8889
EOL

# Edit the file with your specific settings
nano .env
```

### Step 5: Deploy with Docker Compose

```bash
# Start the containers
docker-compose up -d

# Check the status
docker-compose ps
```

### Step 6: Access GearVue

1. Navigate to `http://your-unraid-ip:8889` in your browser
2. You should see the GearVue login page

## Persistent Storage

GearVue on Unraid uses the following persistent storage locations:

| Container Path | Host Path | Purpose |
|----------------|-----------|---------|
| `/app/app/data` | `/mnt/user/appdata/gearvue/data` | Application data (equipment, users, etc.) |
| `/app/logs` | `/mnt/user/appdata/gearvue/logs` | Log files |
| `/app/output` | `/mnt/user/appdata/gearvue/output` | Generated reports and files |
| `/app/Resources` | `/mnt/user/appdata/gearvue/resources` | Resource files |

## Auto-Updates

The Unraid container is configured to auto-update when new releases are available:

1. **Docker Template Method**: Updates are managed through the CA Auto-update plugin (if installed)
2. **Docker Compose Method**: Add to `/boot/config/plugins/dockerMan/notifications/dockerupdates.cron` for auto-update support

## Backups

### Backing Up GearVue Data

1. **Using Unraid Backup**: Include `/mnt/user/appdata/gearvue` in your Unraid backup
2. **Manual Backup**:
   ```bash
   cd /mnt/user/appdata
   tar -czf gearvue_backup_$(date +%Y%m%d).tar.gz gearvue
   ```

### Restoring from Backup

1. Stop the GearVue container
2. Extract the backup:
   ```bash
   cd /mnt/user/appdata
   rm -rf gearvue  # Remove existing data first
   tar -xzf gearvue_backup_YYYYMMDD.tar.gz
   ```
3. Start the GearVue container

## Troubleshooting

### Container Not Starting

Check the container logs in the Unraid web interface or run:
```bash
docker logs gearvue
```

### Can't Access the Web Interface

1. Verify the container is running
2. Check the port mapping in the container settings
3. Ensure no firewall is blocking access to the port

### Email Notifications Not Working

1. Verify your SMTP settings in the container environment variables
2. Check the application logs for email-related errors:
   ```bash
   cat /mnt/user/appdata/gearvue/logs/error_log.txt
   ```

## Advanced Configuration

### Custom Network Configuration

If you need to use a specific IP address or other network configuration:

1. In the Docker template, click "Advanced View"
2. Modify the network settings as needed
3. For multiple network interfaces, consider using the macvlan network type

### External Database

By default, GearVue uses file-based storage. If you want to use an external database:

1. Set up a MySQL/MariaDB container in Unraid
2. Add the following environment variables to the GearVue container:
   - `DB_TYPE=mysql`
   - `DB_HOST=mariadb`  (or your database container name)
   - `DB_NAME=gearvue`
   - `DB_USER=gearvue_user`
   - `DB_PASSWORD=your_password`

## Getting Support

If you encounter issues with the Unraid deployment:

1. Check the container logs
2. Refer to the main GearVue documentation
3. Visit the GearVue GitHub repository for issues and solutions

---

<div align="center">
  <p>GearVue Equipment Tracker Deployment for Unraid</p>
</div>