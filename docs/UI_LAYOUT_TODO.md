# UI Layout Improvements TODO

This document tracks needed improvements to the wider layout implementation.

## Current Status
We've addressed most of the layout issues through the new layout-fixes.css file. Major improvements include:

- Fixed UI element collisions in wider layouts
- Improved button styling and consistency
- Enhanced mobile responsiveness with better breakpoints
- Fixed modal dialog positioning and behavior

## Completed Improvements

### Layout Fixes
- [x] Fixed collision between UI elements in wider layouts
- [x] Better handling of tables that expand beyond their containers
- [x] Fixed modal dialog positioning and widths in wider layouts
- [x] Ensured all containers properly use the width classes

### Button Styling
- [x] Standardized button spacing and sizing
- [x] Fixed action button alignment and overflow issues
- [x] Improved button visibility and clickability on mobile

### Modal Behavior
- [x] Fixed modal backdrop removal when closing modals
- [x] Added proper theme application to modal dialogs
- [x] Implemented mutation observer for dynamically added modals
- [x] Fixed specific issues with QR code modal dark overlay

### Theme Compatibility
- [x] Improved theme icon display across all themes
- [x] Fixed logo appearance in dark themes
- [x] Added dynamic theme application to modals
- [x] Standardized icon styling across themes

## Remaining Tasks

### Responsive Behavior
- [ ] Further mobile layout optimization
- [ ] Additional testing on various devices and screen sizes
- [ ] Implement collapsible tables for very small screens

### Additional Enhancements
- [ ] Add proper table scrolling behavior for very wide tables

## Implementation Plan
Most critical issues have been addressed in the May 2025 update. The remaining tasks will be tackled in future updates, with a focus on enhanced mobile support and table behavior for extremely wide screens.