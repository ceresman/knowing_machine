import time
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def calculate_grid_positions(min_x, max_x, min_y, max_y, zoom_level):
    """Calculate grid positions for systematic capture."""
    # Constants for overlap to ensure no gaps
    OVERLAP_FACTOR = 0.1
    
    # Calculate viewport dimensions at this zoom level
    # These are approximate and will need adjustment based on actual rendering
    viewport_width = 1976  # Target width
    viewport_height = 2114  # Target height
    
    # Calculate step sizes with overlap
    x_step = viewport_width * (1 - OVERLAP_FACTOR)
    y_step = viewport_height * (1 - OVERLAP_FACTOR)
    
    # Generate grid positions
    positions = []
    x = min_x
    while x < max_x:
        y = min_y
        while y < max_y:
            positions.append({
                'x': x,
                'y': y,
                'zoom': zoom_level
            })
            y += y_step
        x += x_step
    
    return positions

def capture_corner_positions(driver, output_dir):
    """Capture specific corner positions."""
    corners = [
        {'x': 156900.14, 'y': 2793.01, 'zoom': 14.8544, 'name': 'rightdown'},
        {'x': 4079.86, 'y': 14209.55, 'zoom': 14.8544, 'name': 'leftup'}
    ]
    
    corners_dir = os.path.join(output_dir, 'corners')
    os.makedirs(corners_dir, exist_ok=True)
    
    for corner in corners:
        url = f"https://calculatingempires.net/?pos={corner['x']:.2f}%2C{corner['y']:.2f}%2C{corner['zoom']:.4f}"
        driver.get(url)
        time.sleep(2)  # Allow rendering to complete
        
        filename = os.path.join(corners_dir, f"{corner['name']}_corner.png")
        driver.save_screenshot(filename)
        print(f"Captured corner position: {filename}")

def verify_output_size(output_dir):
    """Verify that the output is 10x-100x larger than current implementation."""
    base_size = 1976 * 2114  # Current implementation size
    total_size = 0
    
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.png'):
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
    
    size_ratio = total_size / base_size
    print(f"Output size ratio: {size_ratio:.2f}x")
    return 10 <= size_ratio <= 100

def capture_visualization():
    """Capture the full visualization across all zoom levels."""
    # Coordinate boundaries
    COORDINATE_RANGES = {
        'x': (4079.86, 156900.14),
        'y': (2793.01, 14209.55),
        'zoom_levels': {
            'min': 10.0,  # Adjusted to required range
            'max': 15.0,
            'step': 0.5  # Adjusted for finer granularity
        }
    }
    
    # Create output directory
    output_dir = 'captured_visualization'
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup webdriver (assuming Chrome)
    driver = webdriver.Chrome()
    driver.set_window_size(1976, 2114)  # Set to target dimensions
    
    # First capture corner positions
    capture_corner_positions(driver, output_dir)
    
    try:
        # Capture at different zoom levels
        current_zoom = COORDINATE_RANGES['zoom_levels']['min']
        while current_zoom <= COORDINATE_RANGES['zoom_levels']['max']:
            try:
                # Calculate grid positions for this zoom level
                positions = calculate_grid_positions(
                    COORDINATE_RANGES['x'][0],
                    COORDINATE_RANGES['x'][1],
                    COORDINATE_RANGES['y'][0],
                    COORDINATE_RANGES['y'][1],
                    current_zoom
                )
                
                # Create zoom level directory
                zoom_dir = os.path.join(output_dir, f'zoom_{current_zoom:.4f}')
                os.makedirs(zoom_dir, exist_ok=True)
                
                # Capture each position
                for idx, pos in enumerate(positions):
                    try:
                        # Construct URL with position
                        url = f"https://calculatingempires.net/?pos={pos['x']:.2f}%2C{pos['y']:.2f}%2C{pos['zoom']:.4f}"
                        
                        # Navigate and wait for load
                        driver.get(url)
                        time.sleep(2)  # Allow rendering to complete
                        
                        # Take screenshot
                        filename = os.path.join(zoom_dir, f'capture_{idx:04d}.png')
                        driver.save_screenshot(filename)
                        
                        print(f"Captured {filename}")
                    except Exception as e:
                        print(f"Error capturing position {idx} at zoom {current_zoom}: {str(e)}")
                        continue
                
                # Increment zoom level
                current_zoom += COORDINATE_RANGES['zoom_levels']['step']
            except Exception as e:
                print(f"Error processing zoom level {current_zoom}: {str(e)}")
                current_zoom += COORDINATE_RANGES['zoom_levels']['step']
                continue
    
    except Exception as e:
        print(f"Fatal error during capture: {str(e)}")
    finally:
        driver.quit()
        
        # Verify output size
        if verify_output_size(output_dir):
            print("Successfully captured visualization with required size ratio")
        else:
            print("Warning: Output size does not meet 10x-100x requirement")

if __name__ == '__main__':
    capture_visualization()
