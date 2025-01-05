import os
from PIL import Image

def verify_output_size(output_dir):
    """Verify that the output is 10x-100x larger than current implementation."""
    base_size = 1976 * 2114  # Current implementation size
    total_pixels = 0
    file_count = 0
    zoom_stats = {}  # Track pixels per zoom level
    
    # Initialize zoom level tracking
    current_zoom = 12.4515
    while current_zoom <= 18.0000:
        zoom_stats[round(current_zoom, 4)] = {
            'pixels': 0,
            'files': 0,
            'ratio': 0
        }
        current_zoom += 0.66
    
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.png'):
                try:
                    # Extract zoom level from filename or path
                    zoom_level = None
                    for zoom in zoom_stats.keys():
                        if f"_{zoom}" in file or f"/{zoom}/" in root:
                            zoom_level = zoom
                            break
                    
                    with Image.open(os.path.join(root, file)) as img:
                        width, height = img.size
                        pixels = width * height
                        total_pixels += pixels
                        file_count += 1
                        
                        # Track per-zoom statistics
                        if zoom_level:
                            zoom_stats[zoom_level]['pixels'] += pixels
                            zoom_stats[zoom_level]['files'] += 1
                            zoom_stats[zoom_level]['ratio'] = zoom_stats[zoom_level]['pixels'] / base_size
                except Exception as e:
                    print(f"Error processing {file}: {str(e)}")
                    continue
                    
    # Print detailed zoom level statistics
    print("\nPixels per zoom level:")
    for zoom, stats in sorted(zoom_stats.items()):
        if stats['files'] > 0: 
            print(f"Zoom {zoom:.4f}: {stats['pixels']:,} pixels ({stats['ratio']:.2f}x base size) from {stats['files']} files")
    
    size_ratio = total_pixels / base_size
    print(f"\nOutput Size Analysis")
    print("=" * 20)
    print(f"Base Canvas: 1976x2114 ({base_size:,} pixels)")
    print(f"Total Captured Pixels: {total_pixels:,}")
    print(f"Size Ratio: {size_ratio:.2f}x")
    print(f"Requirement (10x-100x): {'✓' if 10 <= size_ratio <= 100 else '✗'} {size_ratio:.2f}x is {'within' if 10 <= size_ratio <= 100 else 'outside'} range")
    
    return 10 <= size_ratio <= 100

if __name__ == '__main__':
    output_dir = 'captured_visualization'
    verify_output_size(output_dir)
