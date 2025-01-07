from PIL import Image
import os
import json
import math
from typing import Dict, List, Tuple

def load_screenshot_info(base_dir: str) -> List[Dict]:
    """Load information about all captured screenshots."""
    screenshots = []
    
    # Process corner positions first
    corners_dir = os.path.join(base_dir, 'corners')
    if os.path.exists(corners_dir):
        for filename in os.listdir(corners_dir):
            if filename.endswith('.png'):
                position = filename.replace('_corner.png', '')
                screenshots.append({
                    'filename': os.path.join(corners_dir, filename),
                    'position': position,
                    'zoom': 14.8544  # Corner positions use this zoom
                })
    
    # Process zoom level captures
    for dirname in os.listdir(base_dir):
        if dirname.startswith('zoom_'):
            zoom_dir = os.path.join(base_dir, dirname)
            if os.path.isdir(zoom_dir):
                zoom_level = float(dirname.replace('zoom_', ''))
                
                for filename in os.listdir(zoom_dir):
                    if filename.endswith('.png'):
                        screenshots.append({
                            'filename': os.path.join(zoom_dir, filename),
                            'position': filename.replace('.png', ''),
                            'zoom': zoom_level
                        })
    
    return screenshots

def calculate_pixel_position(x: float, y: float, zoom: float,
                           min_x: float, min_y: float,
                           canvas_width: int, canvas_height: int) -> Tuple[int, int]:
    """Calculate pixel position based on coordinates and zoom level."""
    # Normalize coordinates to canvas dimensions
    x_normalized = (x - min_x) / (156900.14 - 4079.86)  # Full x range
    y_normalized = (y - min_y) / (14209.55 - 2793.01)   # Full y range
    
    # Apply zoom factor
    zoom_factor = (zoom - 10.0) / (15.0 - 10.0)  # Normalize zoom to 0-1 range
    
    # Calculate pixel positions
    pixel_x = int(x_normalized * canvas_width)
    pixel_y = int(y_normalized * canvas_height)
    
    return pixel_x, pixel_y

def merge_screenshots(screenshots: List[Dict], output_path: str):
    """Merge screenshots into a single large image."""
    # Constants
    BASE_WIDTH = 1976
    BASE_HEIGHT = 2114
    SCALE_FACTOR = 10  # For 10x larger output
    
    # Calculate output dimensions
    output_width = BASE_WIDTH * SCALE_FACTOR
    output_height = BASE_HEIGHT * SCALE_FACTOR
    
    # Create base image
    base_image = Image.new('RGB', (output_width, output_height), 'white')
    
    # Track coverage for overlap handling
    coverage = {}  # (x,y) -> count of overlaps
    
    # Process screenshots
    for screenshot in screenshots:
        try:
            # Load screenshot
            img = Image.open(screenshot['filename'])
            
            # Extract position information
            if isinstance(screenshot['position'], str):
                if screenshot['position'] in ['leftup', 'rightdown']:
                    # Handle corner positions
                    if screenshot['position'] == 'leftup':
                        x, y = 4079.86, 14209.55
                    else:
                        x, y = 156900.14, 2793.01
                else:
                    # Handle grid positions
                    idx = int(screenshot['position'].split('_')[1])
                    # Calculate x,y based on index and grid size
                    x = 4079.86 + (idx % 10) * ((156900.14 - 4079.86) / 10)
                    y = 14209.55 - (idx // 10) * ((14209.55 - 2793.01) / 10)
            
            # Calculate pixel position
            pixel_x, pixel_y = calculate_pixel_position(
                x, y, screenshot['zoom'],
                4079.86, 2793.01,
                output_width, output_height
            )
            
            # Paste image with alpha blending for overlap
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Handle overlap by tracking coverage
            img_width, img_height = img.size
            for px in range(pixel_x, pixel_x + img_width):
                for py in range(pixel_y, pixel_y + img_height):
                    pos = (px, py)
                    if pos in coverage:
                        coverage[pos] += 1
                    else:
                        coverage[pos] = 1
            
            # Paste with alpha blending
            base_image.paste(img, (pixel_x, pixel_y), img)
            
            print(f"Merged {screenshot['filename']}")
            
        except Exception as e: 
            print(f"Error processing {screenshot['filename']}: {str(e)}")
            continue
    
    # Save final image
    base_image.save(output_path)
    print(f"Saved merged image to {output_path}")
    
    # Calculate coverage statistics
    total_pixels = len(coverage)
    avg_overlap = sum(coverage.values()) / total_pixels if total_pixels > 0 else 0
    print(f"Average overlap: {avg_overlap:.2f} screenshots per pixel")
    
    # Verify size requirement
    base_size = BASE_WIDTH * BASE_HEIGHT
    output_size = os.path.getsize(output_path)
    size_ratio = output_size / base_size
    print(f"Output size ratio: {size_ratio:.2f}x")
    
    return size_ratio >= 10 and size_ratio <= 100

if __name__ == '__main__':
    base_dir = 'captured_visualization'
    output_path = 'merged_visualization.png'
    
    screenshots = load_screenshot_info(base_dir)
    if merge_screenshots(screenshots, output_path):
        print("Successfully merged visualization with required size ratio")
    else:
        print("Warning: Output size does not meet 10x-100x requirement")
