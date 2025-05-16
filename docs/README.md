# GearVue Documentation

<div align="center">
  <img src="../Resources/GearVue-Whitebackground.jpg" alt="GearVue Logo" width="400">
  <br>
  <i>Medical Physics Equipment Management System</i>
  <br><br>
</div>

Welcome to the GearVue documentation. This directory contains comprehensive guides for using and deploying the GearVue equipment management system.

## Documentation Index

### User Guides

- [**QR Code System Guide**](QR_CODE_GUIDE.md) - How to use the zero-friction QR code system
- [**Transport Guide**](TRANSPORT_GUIDE.md) - Working with equipment transport requests

### Technical Documentation

- [**Deployment Guide**](DEPLOYMENT_GUIDE.md) - How to deploy GearVue in various environments
- [**Theme System**](THEME_SYSTEM.md) - Documentation of the theme system and how to customize it
- [**Codebase Analysis**](CODEBASE_ANALYSIS.md) - Technical architecture and design decisions
- [**UI Layout TODO**](UI_LAYOUT_TODO.md) - Planned improvements for UI layouts
- [**Code Standards**](CODE_STANDARDS.md) - Coding standards and guidelines for the project
- [**Developer Guide**](DEVELOPER_GUIDE.md) - Development workflow and branch management

### Additional Resources

- [**Project Overview**](../README.md) - Main project documentation and features
- [**Changelog**](CHANGELOG.md) - Version history and changes
- [**Claude Guidance**](CLAUDE.md) - Special guidance for Claude AI when working with this code

## Project Structure

The GearVue application is organized as follows:

```
gearvue/
├── app/                    # Application code
│   ├── data/               # JSON data files
│   ├── models/             # Data managers
│   ├── routes/             # Route handlers
│   ├── static/             # Static assets (CSS, JS, images)
│   └── templates/          # HTML templates
├── docs/                   # Documentation files (you are here)
├── docker/                 # Docker configuration files
├── scripts/                # Utility scripts
├── tests/                  # Test suite
└── README.md               # Project overview
```

## Quick Links

- [Setup Instructions](../README.md#setup-instructions)
- [Running the Application](../README.md#manual-setup)
- [User Accounts](../README.md#user-accounts)
- [Theme Support](../README.md#theme-support)
- [Testing the Application](../README.md#testing-the-application)

## Development

For developers working on GearVue, the following resources are available:

- [**Developer Guide**](DEVELOPER_GUIDE.md) - Comprehensive guide for developers (including branch management)
- [Code Standards](CODE_STANDARDS.md)
- [Running Tests](../README.md#running-tests)
- [Recent Updates](CHANGELOG.md)
- [Known Issues](CLAUDE.md#known-issues)

**IMPORTANT: Never commit directly to the main branch! Always create a feature branch for your changes.**
See the [Developer Guide](DEVELOPER_GUIDE.md) for details on the required development workflow.