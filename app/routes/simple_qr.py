"""
Direct QR code generator for equipment tracking
"""
import os
import sys
import subprocess
import time

def generate_qr_code(url, output_path, equipment_id="", manufacturer="", model="", serial=""):
    """
    Generate a QR code using the shell script without fallbacks

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
        # Get the root directory for the project
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        qrcodes_dir = os.path.join(root_dir, 'qrcodes')

        print(f"QR codes directory: {qrcodes_dir}")
        print(f"Generating QR code with parameters: URL={url}, MFR={manufacturer}, MODEL={model}, SN={serial}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Change to qrcodes directory
        current_dir = os.getcwd()
        os.chdir(qrcodes_dir)

        # Make the script executable
        try:
            subprocess.run(["chmod", "+x", "./generate_qr.sh"], check=True)
        except Exception as e:
            print(f"Warning: couldn't change script permissions: {e}")

        # Run the shell script with arguments
        cmd = [
            "./generate_qr.sh",
            url,
            manufacturer,
            model,
            serial
        ]

        print(f"Running QR generator: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Extract the output path from the script's output
        output_lines = result.stdout.splitlines()
        generated_qr_path = None

        for line in output_lines:
            if "QR code has been generated successfully" in line:
                parts = line.split(": ")
                if len(parts) > 1:
                    generated_qr_path = parts[1].strip()

        if not generated_qr_path:
            # Find the most recent file in Generated_QR
            generated_dir = os.path.join(qrcodes_dir, "Generated_QR")
            if os.path.exists(generated_dir):
                files = [os.path.join(generated_dir, f) for f in os.listdir(generated_dir) if f.endswith('.png')]
                if files:
                    generated_qr_path = max(files, key=os.path.getctime)

        # Return to original directory
        os.chdir(current_dir)

        if generated_qr_path and os.path.exists(os.path.join(qrcodes_dir, generated_qr_path)):
            # Copy to the requested output path
            import shutil
            full_path = os.path.join(qrcodes_dir, generated_qr_path)
            shutil.copy2(full_path, output_path)
            print(f"QR code copied to {output_path}")
            return True, output_path
        else:
            raise Exception("QR code generation failed: No output file found")

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