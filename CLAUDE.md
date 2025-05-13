# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- **Run application**: `python run.py [--host HOST] [--port PORT] [--debug]`
- **Run tests**: `python -m unittest tests/test_equipment_tracker.py`
- **Run single test**: `python -m unittest tests.test_equipment_tracker.TestEquipmentTracker.test_name`
- **Start server with shell script**: `./start.sh`
- **Debug start**: `./start_debug.sh`

## Recent Updates

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

## Code Style Guidelines

- **Imports**: Group imports by standard library, third-party, and local modules with a blank line between groups
- **Docstrings**: Use triple-quotes for module, class, and function docstrings with clear descriptions and Args/Returns sections
- **Error Handling**: Use try/except with specific exceptions and provide meaningful error messages
- **Naming**: Use snake_case for variables/functions, PascalCase for classes
- **Type Hints**: Not currently used but may be added as needed
- **Line Length**: Keep lines to 100 characters or less
- **Formatting**: Use 4 spaces for indentation, not tabs
- **Functions**: Keep functions focused on a single task with descriptive names
- **Comments**: Use comments to explain "why" not "what"