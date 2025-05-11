# GearVue QR Code System

## Overview

The GearVue QR code system provides a completely frictionless way for users to check out, check in, and report issues with equipment without requiring login. This guide explains how to use and implement the QR code system.

> **Zero-Friction Access**: Users can scan QR codes and immediately take action without any login barriers.

## How It Works

1. **Equipment QR Codes**: Each piece of equipment has a unique QR code that links to its landing page.
2. **Mobile-Friendly Interface**: The QR code landing page is optimized for mobile devices.
3. **No Login Required**: Users can perform common actions without needing to log in.

## Generating QR Codes

Administrators and physicists can generate QR codes for equipment:

1. Navigate to the equipment detail page
2. Click on the "Generate QR Code" button
3. Print the generated QR code and affix it to the physical equipment

## QR Code Design

The QR codes have been designed with the following professional elements:

- **Logo Integration**: Incorporates the Mary Bird Perkins flame logo
- **Header**: "Property of Mary Bird Perkins Cancer Center"
- **Footer**: "Department of Medical Physics"
- **Left Side**: Rotated text showing "MFR: [manufacturer]"
- **Right Side**: Rotated text showing "Model: [model]" and "Serial: [serial]"
- **Color Scheme**: All text matches the Mary Bird Perkins flame red color
- **Error Correction**: High error correction level (Level H - up to 30% damage tolerance)

## QR Code Landing Page

When a user scans a QR code, they see a landing page with:

- Equipment details (manufacturer, model, serial number, etc.)
- Current status (checked out or available)
- Equipment condition (green/yellow/red status indicator)
- Quick action buttons

## Available Actions

From the landing page, users can immediately take action without login:

### 1. Check Out Equipment

Users can check out equipment by:
- Clicking the "Check Out Equipment" button
- Selecting their name from a dropdown of common users OR entering their name/initials
- Specifying where the equipment will be used
- Setting an expected return date
- Adding optional notes

The equipment is instantly checked out with no login credentials required!

### 2. Check In Equipment

Users can return equipment by:
- Clicking the "Check In Equipment" button
- Identifying themselves (selecting from dropdown or entering name/initials)
- Specifying where they're returning the equipment to
- Adding optional notes about the equipment's condition

The equipment is instantly checked in without login barriers!

### 3. Submit Tickets/Issues

Users can report problems by:
- Clicking the "Submit Issue/Ticket" button
- Identifying themselves (selecting from dropdown or entering name/initials)
- Selecting an issue type and priority
- Providing a title and description of the issue

The issue is immediately logged with appropriate traffic light status indicators!

## Best Practices

1. **Place QR Codes Prominently**: Affix QR codes in visible locations on the equipment.
2. **Laminate or Protect QR Codes**: Ensure durability in clinical environments.
3. **Educate Users**: Show staff how easy it is to use the QR code system.
4. **Test Periodically**: Ensure QR codes remain scannable and links valid.

## Equipment Condition Indicators

The equipment status is shown with a traffic light system:

- **Green**: Normal - fully operational
- **Yellow**: Warning - needs attention but still usable
- **Red**: Critical - out of service or requires immediate repair

Only administrators and physicists can change equipment condition status through the ticket system.

## Benefits

- **Instant Access**: Users can immediately take action without login barriers
- **Increased Compliance**: Ultra-low friction leads to better equipment tracking
- **Better Visibility**: Easy to see who has equipment and its current condition
- **Reduced Training**: Intuitive interface requires minimal training
- **Improved Reporting**: Issues get reported more quickly with less friction
- **Mobile Optimized**: Designed specifically for smartphones scanning QR codes

## Technical Implementation

The QR code system uses several techniques to ensure completely frictionless access:

1. **Dedicated QR Routes**: Special `/qr` routes bypass all login requirements
2. **CSRF Protection Disabled**: Forms work without security tokens for mobile users
3. **Mobile-First Design**: Templates optimized for smaller touch screens
4. **User Selection**: Simple dropdown or name/initials entry for identification
5. **Traffic Light System**: Visual indicators make equipment status immediately clear