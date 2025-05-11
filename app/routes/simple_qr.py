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
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Create QR image
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Create a larger image with space for text
        img_width, img_height = qr_img.size
        background = Image.new('RGB', (img_width, img_height + 80), color='white')

        # Paste QR code onto background
        background.paste(qr_img, (0, 0))

        # Add text
        draw = ImageDraw.Draw(background)
        try:
            # Try to use a font
            # font = ImageFont.truetype("arial.ttf", 15)
            font = ImageFont.load_default()

            # Create text content
            title_text = "Mary Bird Perkins Cancer Center"
            equipment_text = f"{equipment_id} - {manufacturer} {model} {serial}"

            # Draw title at top
            title_position = (10, img_height + 10)
            draw.text(title_position, title_text, fill="black", font=font)

            # Draw equipment info below
            text_position = (10, img_height + 40)
            draw.text(text_position, equipment_text, fill="black", font=font)

        except Exception as e:
            print(f"Error adding text to QR code: {str(e)}")
            # Continue without text if font fails

        # Save the QR code
        background.save(output_path)
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