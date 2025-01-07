import os
from pathlib import Path
from tile_index_calculation import TileCalculator
from download_tiles import download_tile, OUTPUT_DIR

def test_zoom_coverage():
    """Test tile downloads and coverage for specific zoom levels."""
    calc = TileCalculator()
    
    # Test coordinates from user requirements
    test_cases = [
        (4079.86, 14209.55, 14.8544, "leftup"),
        (156900.14, 2793.01, 14.8544, "rightdown"),
        (93000.24, 8725.0, 12.5511, "min_zoom"),
        (92988.96, 8777.58, 18.0000, "max_zoom")
    ]
    
    for x, y, zoom, case_name in test_cases:
        print(f"\nTesting {case_name} case:")
        print(f"Coordinates: ({x}, {y}) at zoom {zoom}")
        
        # Get tile range and coverage info
        tile_range = calc.get_tile_range(zoom)
        coverage = calc.verify_coordinate_coverage(x, y, zoom)
        
        # Calculate size ratio using tile dimensions
        tile_size = 256
        final_width = (int(tile_range.max_x) - int(tile_range.min_x) + 1) * tile_size
        final_height = (int(tile_range.max_y) - int(tile_range.min_y) + 1) * tile_size
        base_width, base_height = 1976, 2114
        size_ratio = (final_width * final_height) / (base_width * base_height)
        
        print(f"Size ratio: {size_ratio:.2f}x")
        print(f"Final dimensions: {final_width}x{final_height}")
        print(f"Tile range: x={tile_range.min_x}-{tile_range.max_x}, y={tile_range.min_y}-{tile_range.max_y}")
        
        # Test downloading a sample tile
        test_x = int((tile_range.max_x + tile_range.min_x) // 2)
        test_y = int((tile_range.max_y + tile_range.min_y) // 2)
        
        print(f"\nTesting tile download at zoom={zoom}, x={test_x}, y={test_y}")
        success = download_tile(zoom, test_x, test_y)
        
        if success:
            output_path = OUTPUT_DIR / f"{zoom:.4f}" / str(test_x) / f"{test_y}.png"
            print(f"Successfully downloaded tile to {output_path}")
        else:
            print("Failed to download tile")

if __name__ == "__main__":
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    test_zoom_coverage()
