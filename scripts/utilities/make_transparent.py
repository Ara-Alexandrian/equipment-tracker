#!/usr/bin/env python3
"""
Script to create transparent versions of the logo images.
"""
import numpy as np
from PIL import Image
import os

# Paths
input_dir = "Resources"
output_dir = "app/static/img"
temp_dir = "temp_logos"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)

# Process both logo variants
logo_files = ["gearvue-notext.png", "gearvue-text.png"]

for logo_file in logo_files:
    input_path = os.path.join(input_dir, logo_file)
    output_path = os.path.join(output_dir, f"{os.path.splitext(logo_file)[0]}-transparent.png")
    
    # Open the image
    img = Image.open(input_path).convert("RGBA")
    
    # Get the image data as a numpy array
    data = np.array(img)
    
    # Create a mask for white or nearly white pixels (adjust threshold as needed)
    # For RGB channels: if R, G, and B are all above 240, consider it white
    r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]
    white_mask = (r > 240) & (g > 240) & (b > 240)
    
    # Set alpha channel to 0 (transparent) for white pixels
    data[:, :, 3] = np.where(white_mask, 0, 255)
    
    # Convert back to an image
    transparent_img = Image.fromarray(data)
    
    # Save the transparent image
    transparent_img.save(output_path)
    print(f"Created transparent version: {output_path}")

print("Done creating transparent logo versions!")