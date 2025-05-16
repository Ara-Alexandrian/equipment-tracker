"""
QR Code generation helper utilities
This module provides a direct QR code generation function that doesn't rely on external scripts
"""
import os
import sys
import tempfile
import subprocess
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def generate_qr_code_direct(url, output_path, equipment_id="", manufacturer="", model="", serial=""):
    """
    Generate a QR code directly using the qrcode library without relying on external scripts
    
    Args:
        url: URL to encode in the QR code
        output_path: Path where to save the QR code
        equipment_id: Equipment ID
        manufacturer: Manufacturer name
        model: Model number
        serial: Serial number
        
    Returns:
        Tuple of (success, result_path_or_error_message)
    """
    try:
        # Create the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Add the equipment information text
        if equipment_id or manufacturer or model or serial:
            # Convert to RGB for text addition
            rgb_img = qr_img.convert('RGB')
            
            # Get image dimensions
            img_width, img_height = rgb_img.size
            
            # Create a new canvas with space below for the text
            text_height = 60  # space for text
            new_img = Image.new('RGB', (img_width, img_height + text_height), color='white')
            
            # Paste the QR code on top
            new_img.paste(rgb_img, (0, 0))
            
            # Add text information
            draw = ImageDraw.Draw(new_img)
            
            # Try to load a font, default to a simple one if not found
            try:
                font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'static', 'fonts', 'opensans-regular.ttf')
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 12)
                else:
                    font = ImageFont.load_default()
            except Exception:
                font = ImageFont.load_default()
            
            # Add text
            text_y = img_height + 5
            if equipment_id:
                draw.text((10, text_y), f"ID: {equipment_id}", fill='black', font=font)
                text_y += 15
            
            if manufacturer or model:
                draw.text((10, text_y), f"{manufacturer} {model}".strip(), fill='black', font=font)
                text_y += 15
                
            if serial:
                draw.text((10, text_y), f"SN: {serial}", fill='black', font=font)
            
            # Save the new image
            new_img.save(output_path)
        else:
            # Save the QR code without additional text
            qr_img.save(output_path)
            
        return True, output_path
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, str(e)

# Fallback function that tries different QR generation methods
def generate_qr_code_fallback(url, output_path, equipment_id="", manufacturer="", model="", serial=""):
    """
    Tries multiple QR code generation methods to ensure one works
    
    Args:
        url: URL to encode in the QR code
        output_path: Path where to save the QR code
        equipment_id: Equipment ID
        manufacturer: Manufacturer name
        model: Model number
        serial: Serial number
        
    Returns:
        Tuple of (success, result_path_or_error_message)
    """
    # First try the direct method
    success, result = generate_qr_code_direct(url, output_path, equipment_id, manufacturer, model, serial)
    if success:
        return True, result
    
    # If direct method failed, try an even simpler method
    try:
        # Create the most basic QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create QR code image and save
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        
        return True, output_path
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = f"All QR generation methods failed. Last error: {str(e)}"
        return False, error_msg
        
# Function to validate that the QR code was actually created
def validate_qr_output(output_path):
    """Check if the QR code file exists and is valid"""
    if not os.path.exists(output_path):
        return False, "QR code file does not exist"
    
    try:
        # Try to open and validate the image
        img = Image.open(output_path)
        img.verify()  # Verify that it's a valid image
        return True, "QR code is valid"
    except Exception as e:
        return False, f"QR code file exists but is not a valid image: {str(e)}"