# Claude Guidance

<div align="center">
  <img src="../Resources/GearVue-Whitebackground.jpg" alt="GearVue Logo" width="400">
  <br>
  <i>Guidance for Claude AI when working with this codebase</i>
  <br><br>
</div>

This file provides guidance to Claude (claude.ai) when working with code in this repository.

## Commands

These commands are useful for running and testing the application:

- **Run application**: `python run.py [--host HOST] [--port PORT] [--debug]`
- **Run tests**: `python -m unittest tests/test_equipment_tracker.py`
- **Run single test**: `python -m unittest tests.test_equipment_tracker.TestEquipmentTracker.test_name`
- **Start server with shell script**: `./start.sh`
- **Debug start**: `./start_debug.sh`

## Recent Updates

### Auto Reports System (May 2025)
- **Automated Reporting**: New system for scheduled automatic report generation
- **Multiple Formats**: Support for PDF, CSV, and Excel report formats
- **Email Distribution**: Configurable email delivery to different user groups
- **Storage Management**: Automatic archiving with retention period configuration
- **Implementation**: See `/app/routes/auto_reports.py` and `/app/models/auto_reports.py` for implementation

### Transport Request System (May 2025)
- **Equipment Movement**: New system for requesting, approving, and tracking equipment transport between locations
- **Mobile-Optimized**: Zero-friction QR code integration for transport requests
- **Visual Indicators**: Equipment lists show transport status with truck icon badges
- **Dashboard Integration**: Main dashboard shows pending transport requests
- **Implementation**: See `/app/routes/transport.py` and `/app/models/transport_request.py` for implementation

### Theme System (May 2025)
- **Theme Persistence**: Application now properly maintains theme selection (Light/Dark/Dracula) across page navigation
- **Custom Dracula Icon**: The Dracula theme uses a custom SVG icon (`/Resources/dracula-icon.svg`)
- **Theme Icons**: Light mode uses sun icon, Dark mode uses moon icon, Dracula mode uses custom vampire icon
- **Implementation**: See `/app/static/js/theme-unified.js` for the implementation

### Known Issues
- **Equipment Editing**: When editing existing equipment items, the form may not pre-fill with the current values (marked for fixing)

## Important Project Information

- Project uses a JSON-based data storage system with files in `app/data/`
- The QR code system intentionally bypasses login for ease of use
- The theme system persists user preferences in localStorage

## Code Style Guidelines

For detailed coding standards, please refer to [CODE_STANDARDS.md](CODE_STANDARDS.md).

Key points to remember:
- **Imports**: Group imports by standard library, third-party, and local modules with a blank line between groups
- **Docstrings**: Use triple-quotes for module, class, and function docstrings with clear descriptions and Args/Returns sections
- **Error Handling**: Use try/except with specific exceptions and provide meaningful error messages
- **Naming**: Use snake_case for variables/functions, PascalCase for classes
- **Line Length**: Keep lines to 100 characters or less
- **Formatting**: Use 4 spaces for indentation, not tabs
- **Functions**: Keep functions focused on a single task with descriptive names
- **Comments**: Use comments to explain "why" not "what"