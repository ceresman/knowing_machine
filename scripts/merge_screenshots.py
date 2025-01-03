#!/usr/bin/env python3
import os
from PIL import Image
import re
from typing import List, Tuple, Dict, Optional

def parse_coordinates(filename: str) -> Optional[Tuple[float, float, float]]:
    """Extract x, y coordinates and zoom level from filename."""
    match = re.search(r'x(\d+\.?\d*)_y(\d+\.?\d*)_z(\d+\.?\d*)', filename)
    if match:
        return float(match.group(1)), float(match.group(2)), float(match.group(3))
    return None

def compute_image_bounds(screenshots_dir: str) -> Tuple[float, float, float, float]:
    """Compute the min/max coordinates of all screenshots."""
    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')
    
    for filename in os.listdir(screenshots_dir):
        if filename.endswith('.png'):
            coords = parse_coordinates(filename)
            if coords:
                x, y, _ = coords
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    
    return min_x, min_y, max_x, max_y

def normalize_coordinates(x: float, y: float, bounds: Tuple[float, float, float, float]) -> Tuple[int, int]:
    """Convert world coordinates to pixel coordinates."""
    min_x, min_y, max_x, max_y = bounds
    # Scale factor to convert coordinate units to pixels
    x_scale = 1504 / (max_x - min_x)  # viewport width
    y_scale = 869 / (max_y - min_y)   # viewport height
    
    pixel_x = int((x - min_x) * x_scale)
    pixel_y = int((y - min_y) * y_scale)
    return pixel_x, pixel_y

def merge_screenshots(screenshots_dir: str, output_path: str):
    """Merge all screenshots into a single large image."""
    # Compute coordinate bounds
    bounds = compute_image_bounds(screenshots_dir)
    min_x, min_y, max_x, max_y = bounds
    
    # Calculate final image dimensions
    x_range = max_x - min_x
    y_range = max_y - min_y
    x_scale = 1504 / x_range  # viewport width
    y_scale = 869 / y_range   # viewport height
    
    width = int(x_range * x_scale)
    height = int(y_range * y_scale)
    
    # Create blank canvas
    merged = Image.new('RGB', (width, height), 'white')
    
    # Process each screenshot
    for filename in sorted(os.listdir(screenshots_dir)):
        if not filename.endswith('.png'):
            continue
            
        coords = parse_coordinates(filename)
        if not coords:
            continue
            
        x, y, _ = coords
        pixel_x, pixel_y = normalize_coordinates(x, y, bounds)
        
        # Load and paste screenshot
        img_path = os.path.join(screenshots_dir, filename)
        try:
            img = Image.open(img_path)
            # Handle overlap by alpha blending
            merged.paste(img, (pixel_x, pixel_y), mask=None)
            print(f"Merged {filename} at position ({pixel_x}, {pixel_y})")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    # Save merged result
    merged.save(output_path)
    print(f"Saved merged image to {output_path}")

if __name__ == "__main__":
    screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
    output_path = os.path.join(os.path.dirname(__file__), "merged_visualization.png")
    merge_screenshots(screenshots_dir, output_path)
