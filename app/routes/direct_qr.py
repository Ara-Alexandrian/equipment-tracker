"""
Direct QR code generator for equipment tracking.
Import and use simple_qr.py generator for consistency.
"""
from .simple_qr import generate_qr_code

# Set up an alias for backward compatibility
generate_direct_qr = generate_qr_code