#!/usr/bin/env python
"""
Test script for QR code generation
"""
import os
import time
from app.routes.simple_qr import generate_qr_code

# Ensure the QR code directory exists
qr_dir = os.path.join('app', 'static', 'qrcodes')
os.makedirs(qr_dir, exist_ok=True)

# Generate a test QR code with timestamp to make it unique
timestamp = int(time.time())
test_url = f"https://mbpcc.org/equipment/TEST-1234?t={timestamp}"
output_path = os.path.join(qr_dir, f"test_qr_{timestamp}.png")

print(f"Testing QR code generation...")
print(f"URL: {test_url}")
print(f"Output: {output_path}")

# Generate QR code with equipment info
success, result = generate_qr_code(
    test_url,
    output_path,
    equipment_id="TEST-1234",
    manufacturer="IBA",
    model="F65-G",
    serial="555123"
)

if success:
    print(f"SUCCESS: QR code generated at {result}")
    if os.path.exists(result):
        print(f"File size: {os.path.getsize(result)} bytes")
    else:
        print(f"ERROR: File does not exist at {result}")
else:
    print(f"ERROR: QR code generation failed: {result}")