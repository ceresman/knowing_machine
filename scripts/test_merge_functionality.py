import os
import signal
import shutil
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Tuple
from PIL import Image
from merge_visualization import merge_tiles, verify_coordinate_range, apply_transform_matrix

# Constants for testing
BASE_WIDTH = 1976
BASE_HEIGHT = 2114
TRANSFORM_MATRIX = (0.5, 0.0, 0.0, 0.5, 0.0, 0.0)
MIN_SIZE_RATIO = 10
MAX_SIZE_RATIO = 100

# Coordinate ranges
MIN_X, MAX_X = 4079.86, 156900.14
MIN_Y, MAX_Y = 2793.01, 14209.55
MIN_ZOOM, MAX_ZOOM = 12.4515, 18.0000

def verify_transform_matrix(x: float, y: float, width: int, height: int) -> bool:
    """
    Verify that the transform matrix is correctly applied to coordinates.
    Takes into account the scale factor for output size requirements.
    """
    # Scale coordinates to match output size requirements
    scale = (width * height) / (BASE_WIDTH * BASE_HEIGHT)
    scale_factor = (scale ** 0.5) * 0.5  # Compensate for 0.5 transform
    
    # Apply transform with scaling
    tx, ty = apply_transform_matrix(x * scale_factor, y * scale_factor, TRANSFORM_MATRIX)
    return (0 <= tx <= width) and (0 <= ty <= height)

def verify_size_requirements(width: int, height: int) -> bool:
    """Verify that the output image meets size requirements."""
    output_pixels = width * height
    base_pixels = BASE_WIDTH * BASE_HEIGHT
    size_ratio = output_pixels / base_pixels
    return MIN_SIZE_RATIO <= size_ratio <= MAX_SIZE_RATIO

def verify_coordinate_bounds(x: float, y: float, zoom: float) -> bool:
    """Verify that coordinates are within valid bounds."""
    return (MIN_X <= x <= MAX_X and 
            MIN_Y <= y <= MAX_Y and 
            MIN_ZOOM <= zoom <= MAX_ZOOM)

class TimeoutException(Exception):
    pass

@contextmanager
def timeout(seconds):
    def timeout_handler(signum, frame):
        raise TimeoutException(f"Test timed out after {seconds} seconds")
    
    # Set the timeout handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)

def test_merge_with_sample():
    """Test merging functionality with a sample tile."""
    print("\nStarting test_merge_with_sample")
    
    # Initialize paths
    test_dir = Path("test_tiles")
    output_dir = Path("test_output")
    output_path = output_dir / "merged.png"
    
    print("Setting up test directories")
    try:
        # Clean up any existing directories
        for directory in [test_dir, output_dir]:
            if directory.exists():
                print(f"Cleaning up existing directory: {directory}")
                shutil.rmtree(directory)
            print(f"Creating directory: {directory}")
            directory.mkdir(exist_ok=True)

        with timeout(30):  # Set 30-second timeout
            
            # Test multiple zoom levels and coordinates
            test_cases = [
                # Format: (zoom, x, y, description)
                ("12.4515", "4079", "14209", "leftup corner min zoom"),
                ("13.1115", "50000", "10000", "quarter point zoom+1"),
                ("13.7715", "75000", "7500", "quarter point zoom+2"),
                ("14.8544", "156900", "2793", "rightdown corner mid zoom"),
                ("16.0000", "125000", "5000", "three-quarter point"),
                ("17.0000", "140000", "3500", "near max zoom"),
                ("18.0000", "100000", "8000", "middle point max zoom")
            ]
            
            # Create test tiles for each case
            for zoom_level, x_coord, y_coord, desc in test_cases:
                # Verify coordinates are in valid range (with tolerance for integer rounding)
                assert verify_coordinate_range(float(x_coord), float(y_coord), tolerance=1.0), \
                    f"Invalid coordinates ({x_coord}, {y_coord}) for {desc}"
    
                # Create directory structure and test tile
                zoom_dir = test_dir / zoom_level
                zoom_dir.mkdir(exist_ok=True)
                x_dir = zoom_dir / x_coord
                x_dir.mkdir(exist_ok=True)
                
                # Create test tile with coordinates encoded in color
                r = min(255, int(float(x_coord) / 1000))
                b = min(255, int(float(y_coord) / 1000))
                test_tile = Image.new('RGBA', (256, 256), (r, 0, b, 255))
                test_tile.save(x_dir / f"{y_coord}.png")
                print(f"Created test tile for {desc}: zoom={zoom_level}, pos=({x_coord}, {y_coord})")
    
            # Run merge tiles
            image, meets_requirements = merge_tiles(str(test_dir), str(output_path))
            print(f"\nMerge completed successfully")
            print(f"Output meets size requirements: {meets_requirements}")
            assert os.path.exists(output_path), "Output file was not created"
            
            # Verify transform matrix application
            output_image = Image.open(output_path)
            width, height = output_image.size
            
            # Test transform matrix at various points
            test_points = [
                (0, 0),                                    # Origin
                (width//2, height//2),                     # Center
                (width, height),                           # Bottom right
                (width//4, height//4),                     # Top left quadrant
                (width*3//4, height*3//4),                 # Bottom right quadrant
                (width//8, height//8),                     # Fine-grained points
                (width*7//8, height*7//8),
                (width//3, height*2//3),                   # Asymmetric points
                (width*2//3, height//3),
                (width-1, 0),                             # Edge cases
                (0, height-1),
                (width-1, height-1)
            ]
            
            for x, y in test_points:
                assert verify_transform_matrix(float(x), float(y), width, height), \
                    f"Transform matrix verification failed at ({x}, {y})"
            
            # Verify output size requirements
            output_pixels = width * height
            base_pixels = BASE_WIDTH * BASE_HEIGHT
            size_ratio = output_pixels / base_pixels
            print(f"\nOutput dimensions: {width}x{height}")
            print(f"Base dimensions: {BASE_WIDTH}x{BASE_HEIGHT}")
            print(f"Size ratio: {size_ratio:.2f}x")
            
            assert size_ratio >= MIN_SIZE_RATIO, \
                f"Output size ratio {size_ratio:.2f}x is below minimum requirement of {MIN_SIZE_RATIO}x"
            assert size_ratio <= MAX_SIZE_RATIO, \
                f"Output size ratio {size_ratio:.2f}x exceeds maximum requirement of {MAX_SIZE_RATIO}x"
            
            # Clean up
            output_image.close()
            
    except TimeoutException:
        print("Test timed out after 30 seconds")
        raise
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise
        
    finally:
        # Clean up test directories
        for directory in [test_dir, output_dir]:
            if directory.exists():
                try:
                    shutil.rmtree(directory)
                except Exception as e:
                    print(f"Warning: Failed to clean up {directory}: {e}")

if __name__ == '__main__':
    test_merge_with_sample()
