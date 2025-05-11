"""
Simple QR code generator that doesn't rely on complex dependencies
"""
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import time

def generate_simple_qr(url, output_path, equipment_id="", manufacturer="", model="", serial=""):
    """Generate a simple QR code without requiring complex dependencies"""
    try:
        # Generate a basic QR code (simplest possible approach)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        
        print(f"QR code saved to {output_path}")
        return True, output_path
    except Exception as e:
        print(f"Error generating QR code: {str(e)}")
        return False, str(e)

if __name__ == "__main__":
    # Test QR generation
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'qrcodes')
    os.makedirs(output_dir, exist_ok=True)
    
    test_url = "https://example.com/test"
    test_output = os.path.join(output_dir, f"test_qr_{int(time.time())}.png")
    
    success, result = generate_simple_qr(
        test_url, 
        test_output,
        equipment_id="TEST-1234",
        manufacturer="Test Mfr",
        model="Test Model",
        serial="12345"
    )
    
    if success:
        print(f"Test QR code generated successfully at {result}")
    else:
        print(f"Test QR code generation failed: {result}")