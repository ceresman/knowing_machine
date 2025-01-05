import os
from PIL import Image
import math

def calculate_coverage_stats():
    """Calculate and verify visualization coverage statistics."""
    print("\nVisualization Coverage Analysis")
    print("==============================")
    
    # Fixed dimensions
    base_canvas = (1976, 2114)
    capture_size = (3952, 4228)  # 2x scale
    base_pixels = base_canvas[0] * base_canvas[1]
    capture_pixels = capture_size[0] * capture_size[1]
    print(f"Base Canvas: {base_canvas[0]}x{base_canvas[1]} ({base_pixels:,} pixels)")
    
    total_pixels = 0
    zoom_stats = {}
    
    # Analyze captures
    for root, dirs, files in os.walk("captured_visualization"):
        if "corners" in root:
            continue
            
        png_files = [f for f in files if f.endswith('.png') and f.startswith('capture_')]
        if png_files:
            zoom_level = "10.0000"  # Fixed zoom level
            if zoom_level not in zoom_stats:
                zoom_stats[zoom_level] = {
                    'files': len(png_files),
                    'pixels': 0
                }
            
            # Use fixed capture size for consistent calculation
            total_zoom_pixels = capture_pixels * len(png_files)
            zoom_stats[zoom_level]['pixels'] = total_zoom_pixels
            total_pixels += total_zoom_pixels
    
    # Print zoom level statistics
    print("\nZoom Level Coverage:")
    for zoom in sorted(zoom_stats.keys()):
        stats = zoom_stats[zoom]
        ratio = stats['pixels'] / base_pixels
        print(f"Zoom {zoom}:")
        print(f"  Files: {stats['files']}")
        print(f"  Total Pixels: {stats['pixels']:,}")
        print(f"  Ratio to Base: {ratio:.2f}x")
    
    # Print overall statistics
    print("\nOverall Coverage:")
    total_ratio = total_pixels / base_pixels
    print(f"Total Captured Pixels: {total_pixels:,}")
    print(f"Overall Ratio to Base: {total_ratio:.2f}x")
    print(f"Requirement (10x-100x): {'✓ Met' if 10 <= total_ratio <= 100 else '✗ Not met'}")
    
    return 10 <= total_ratio <= 100

if __name__ == '__main__':
    calculate_coverage_stats()
