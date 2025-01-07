from merge_visualization import merge_tiles, MIN_ZOOM, MAX_ZOOM
import os
import shutil
from pathlib import Path
from PIL import Image

def create_test_tiles():
    """Create test tiles at different zoom levels and coordinates."""
    test_dir = Path('test_data')
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    # Create test tiles at different zoom levels
    zoom_levels = [14.8544]  # Start with the specific zoom level from coordinates
    
    # Test coordinates from user requirements
    corners = [
        (4079.86, 14209.55),  # leftup
        (156900.14, 2793.01),  # rightdown
        (93000.24, 8725.00),   # middle point
    ]
    
    for zoom in zoom_levels:
        zoom_dir = test_dir / f"{zoom:.4f}"
        zoom_dir.mkdir()
        
        for x, y in corners:
            x_dir = zoom_dir / str(int(x))
            x_dir.mkdir(exist_ok=True)
            
            # Create test tile
            tile_path = x_dir / f"{int(y)}.png"
            tile = Image.new('RGBA', (256, 256))
            
            # Color corners differently for visual verification
            if (x, y) == corners[0]:  # leftup
                color = (0, 0, 255, 255)  # blue
            elif (x, y) == corners[1]:  # rightdown
                color = (255, 0, 0, 255)  # red
            else:  # middle
                color = (0, 255, 0, 255)  # green
                
            tile.paste(Image.new('RGBA', (256, 256), color), (0, 0))
            tile.save(tile_path)
            
            print(f"Created test tile at zoom {zoom:.4f}, pos ({x}, {y})")

def verify_output_image(image_path: str):
    """Verify the output image meets all requirements."""
    if not os.path.exists(image_path):
        print("Error: Output image not found!")
        return False
        
    # Check file size requirements
    output_size = os.path.getsize(image_path)
    base_size = 1976 * 2114
    size_ratio = output_size / base_size
    print(f"\nSize verification:")
    print(f"Output size: {output_size:,} bytes")
    print(f"Base size: {base_size:,} bytes")
    print(f"Size ratio: {size_ratio:.2f}x")
    print(f"Meets size requirements (10x-100x): {10 <= size_ratio <= 100}")
    
    # Check image dimensions
    with Image.open(image_path) as img:
        width, height = img.size
        print(f"\nDimension verification:")
        print(f"Output dimensions: {width}x{height}")
        print(f"Base dimensions: 1976x2114")
        print(f"Width ratio: {width/1976:.2f}x")
        print(f"Height ratio: {height/2114:.2f}x")
        
        # Verify transform matrix effect (should be 0.5x)
        print(f"\nTransform matrix verification:")
        print(f"Expected scale: 0.5")
        print(f"Actual width scale: {(width/1976)*0.5:.2f}")
        print(f"Actual height scale: {(height/2114)*0.5:.2f}")
    
    return True

def main():
    """Test the merge_tiles implementation."""
    print("Creating test tiles...")
    create_test_tiles()
    
    print("\nTesting merge_tiles implementation...")
    output_path = 'test_merged.png'
    if os.path.exists(output_path):
        os.remove(output_path)
    
    try:
        merged_image, meets_requirements = merge_tiles('test_data', output_path)
        if merged_image is None:
            print("Error: merge_tiles returned None for merged_image!")
            return
            
        print("\nMerge completed successfully!")
        print(f"Meets requirements: {meets_requirements}")
        
        # Verify output
        verify_output_image(output_path)
        
    except Exception as e:
        print(f"Error during merge: {str(e)}")
    finally:
        # Clean up test data
        if os.path.exists('test_data'):
            shutil.rmtree('test_data')

if __name__ == '__main__':
    main()
