"""
QR code generator that integrates with the advanced QR code generator
"""
import os
import sys
import time

def generate_simple_qr(url, output_path, equipment_id="", manufacturer="", model="", serial=""):
    """Generate a fancy QR code using the advanced generator"""
    try:
        # Add qrcodes directory to the system path
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        qrcodes_dir = os.path.join(root_dir, 'qrcodes')
        sys.path.append(qrcodes_dir)
        
        # Import the create_qr_in_flame function
        try:
            from qr_generator import create_qr_in_flame
            print(f"Successfully imported create_qr_in_flame from {qrcodes_dir}")
        except ImportError as e:
            print(f"Error importing qr_generator: {e}")
            return False, f"Error importing qr_generator: {e}"
        
        # Find the logo file
        logo_path = os.path.join(qrcodes_dir, 'Resources', 'Mary Bird Perkins Cancer Center.png')
        
        if not os.path.exists(logo_path):
            print(f"Logo file not found at {logo_path}")
            return False, f"Logo file not found at {logo_path}"
        
        # Create the QR code using the advanced generator
        print(f"Generating QR code with parameters: URL={url}, MFR={manufacturer}, MODEL={model}, SN={serial}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            # Generate the QR code
            output_file = create_qr_in_flame(
                logo_path=logo_path,
                url=url,
                output_path=output_path,
                manufacturer=manufacturer,
                model=model,
                serial=serial
            )
            
            print(f"QR code successfully generated at {output_file}")
            return True, output_file
            
        except Exception as e:
            print(f"Error in create_qr_in_flame: {e}")
            return False, f"Error generating QR code: {e}"
        
    except Exception as e:
        print(f"Error generating QR code: {e}")
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