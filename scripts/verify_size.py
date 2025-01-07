from PIL import Image
import os
import math

def calculate_total_pixels(directory):
    """Calculate total unique pixels across all captured images."""
    total_pixels = 0
    processed_images = set()
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.png'):
                filepath = os.path.join(root, file)
                if filepath not in processed_images:
                    with Image.open(filepath) as img:
                        width, height = img.size
                        total_pixels += width * height
                        processed_images.add(filepath)
    
    return total_pixels

def verify_size_requirements():
    """Verify that the total captured data meets size requirements."""
    base_size = 1976 * 2114  # Original canvas size
    captured_size = calculate_total_pixels('captured_visualization')
    
    size_ratio = captured_size / base_size
    print(f"\nSize Verification Results:")
    print(f"Base canvas size: {base_size:,} pixels")
    print(f"Total captured size: {captured_size:,} pixels")
    print(f"Size ratio: {size_ratio:.2f}x")
    print(f"Requirement (10x-100x): {'✓ Met' if 10 <= size_ratio <= 100 else '✗ Not met'}")
    
    return 10 <= size_ratio <= 100

if __name__ == '__main__':
    verify_size_requirements()
