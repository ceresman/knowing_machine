import os
import math
import requests
import time
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Tuple, Union
from tile_index_calculation import TileCalculator, TileIndex

@dataclass
class TileTask:
    zoom: float  # Changed to float for precise zoom levels
    x: int
    y: int
    future: Optional[Future] = None
    success: bool = False

BASE_URL = "https://tiles.calculatingempires.net/tiles_directory_black_10"  # Single slash for testing
OUTPUT_DIR = Path("downloaded_tiles")

def generate_zoom_levels() -> List[float]:
    """Generate zoom levels that will produce output between 10x-100x larger."""
    # Calculate zoom levels that will give us 10x-100x size ratios
    # Each zoom level doubles the size in both dimensions
    # So going from zoom N to N+1 increases area by 4x
    
    # Start with minimum zoom and calculate steps
    min_zoom = 12.4515  # Confirmed minimum zoom
    max_zoom = 18.0000  # Confirmed maximum zoom
    
    # Calculate zoom steps that give us size ratios between 10x and 100x
    # At zoom level N, size ratio is approximately 4^(N-base_zoom)
    base_zoom = min_zoom
    target_ratios = [10, 25, 50, 75, 100]  # More granular steps
    zoom_levels = []
    
    for ratio in target_ratios:
        # Calculate zoom level needed for this ratio
        # ratio = 4^(zoom_delta), so zoom_delta = log4(ratio)
        zoom_delta = math.log(ratio, 4)
        zoom = round(base_zoom + zoom_delta, 4)
        if min_zoom <= zoom <= max_zoom:
            zoom_levels.append(zoom)
    
    print("Generated zoom levels:")
    for zoom in zoom_levels:
        ratio = 4 ** (zoom - base_zoom)
        print(f"Zoom {zoom:.4f} -> ~{ratio:.1f}x size ratio")
    
    return sorted(zoom_levels)

def download_tile(zoom: float, x: int, y: int) -> bool:
    """Download a single tile and save it to the appropriate directory."""
    # Convert zoom to integer for URL (floor to ensure we don't exceed max zoom)
    zoom_int = int(zoom)
    # In OpenLayers, Y index is negative and inverted: -1 - y
    # But y is already negative in our coordinate system, so we use abs(y)
    y_index = -1 - abs(y)
    url = f"{BASE_URL}/{zoom_int}/{x}/{y_index}.png"
    # Use float zoom for directory structure to maintain precision
    output_path = OUTPUT_DIR / f"{zoom:.4f}" / str(x)
    output_file = output_path / f"{abs(y)}.png"
    
    print(f"Attempting to download tile: zoom={zoom:.4f} (url_zoom={zoom_int})")
    print(f"Coordinates: x={x}, y={y}")
    print(f"Y-index for URL: {y_index}")
    print(f"URL: {url}")
    
    if output_file.exists():
        return True
    
    try:
        # Add headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://calculatingempires.net/',
            'Cache-Control': 'no-cache'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            print(f"Tile not found: zoom={zoom:.4f}, x={x}, y={y} (y_index={y_index})")
            return False
        elif response.status_code != 200:
            print(f"Error {response.status_code} downloading tile: zoom={zoom:.4f}, x={x}, y={y}")
            return False
        
        output_path.mkdir(parents=True, exist_ok=True)
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Downloaded tile: zoom={zoom:.4f} (url_zoom={zoom_int}), x={x}, y={y} (y_index={y_index})")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def get_tile_range(zoom: float) -> TileIndex:
    """Get the tile range for a given zoom level using TileCalculator."""
    calculator = TileCalculator()
    return calculator.get_tile_range(zoom)

def get_progress_file(zoom: float) -> Path:
    """Get the progress file path for a zoom level."""
    return OUTPUT_DIR / f"progress_{zoom:.4f}.txt"

def save_progress(zoom: float, x: int, y: int):
    """Save the current progress for a zoom level."""
    with open(get_progress_file(zoom), 'w') as f:
        f.write(f"{x},{y}")

def load_progress(zoom: float) -> tuple[int, int]:
    """Load the progress for a zoom level."""
    progress_file = get_progress_file(zoom)
    if progress_file.exists():
        with open(progress_file) as f:
            x, y = map(int, f.read().strip().split(','))
            return x, y
    return 0, 0

def check_tile_exists(zoom: float, x: int, y: int) -> bool:
    """Check if a tile exists at the given coordinates."""
    zoom_int = int(zoom)  # Convert zoom to integer for URL
    url = f"{BASE_URL}/{zoom_int}/{x}/{-1-y}.png"  # Use negative Y indexing
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def process_tile_batch(batch: List[TileTask], max_retries: int) -> List[bool]:
    """Process a batch of tiles with retries."""
    results = []
    for task in batch:
        try:
            if task.future:
                success = task.future.result(timeout=10)
                if not success and max_retries > 0:
                    for _ in range(max_retries):
                        if download_tile(task.zoom, task.x, task.y):
                            success = True
                            break
                        time.sleep(1)
                task.success = success
                results.append(success)
        except Exception as e:
            print(f"Error downloading tile z={task.zoom} x={task.x} y={task.y}: {e}")
            task.success = False
            results.append(False)
    return results

def download_zoom_level(zoom: float):
    """Download all tiles for a specific zoom level."""
    calculator = TileCalculator()
    tile_range = get_tile_range(zoom)
    max_retries = 3
    start_x, start_y = load_progress(zoom)
    
    print(f"Processing zoom level {zoom:.4f}...")
    max_x = int(tile_range.max_x)  # Convert to int for tile indices
    max_y = int(tile_range.max_y)
    min_x = int(tile_range.min_x)
    min_y = int(tile_range.min_y)
    
    # Validate tile range
    if max_x < min_x or max_y < min_y:
        print(f"Invalid tile range for zoom level {zoom:.4f}")
        return
    
    # Calculate size ratio using tile dimensions
    tile_size = 256  # OpenLayers default tile size
    final_width = (max_x - min_x + 1) * tile_size
    final_height = (max_y - min_y + 1) * tile_size
    base_width = 1976  # Original canvas width
    base_height = 2114  # Original canvas height
    
    size_ratio = (final_width * final_height) / (base_width * base_height)
    print(f"Size ratio at zoom {zoom:.4f}: {size_ratio:.2f}x")
    print(f"Final dimensions: {final_width}x{final_height}")
    
    if not (10 <= size_ratio <= 100):
        print(f"Warning: Size ratio {size_ratio:.2f}x is outside target range (10x-100x)")
        if size_ratio < 10:
            print("Skipping zoom level - output would be too small")
            return
    
    total_tiles = (max_x - min_x + 1) * (max_y - min_y + 1)
    downloaded = 0
    
    print(f"Starting zoom level {zoom:.4f} from position x={start_x}, y={start_y}")
    print(f"Valid tile range: x={min_x}-{max_x}, y={min_y}-{max_y}")
    print(f"Total tiles to process: {total_tiles}")
    print(f"Final dimensions: {final_width}x{final_height}")
    
    batch_size = 4
    with ThreadPoolExecutor(max_workers=4) as executor:
        for x in range(max(start_x, min_x), max_x + 1):
            y_start = start_y if x == start_x else min_y
            current_batch: List[TileTask] = []
            
            for y in range(max(y_start, min_y), max_y + 1):
                task = TileTask(zoom=zoom, x=x, y=y)
                task.future = executor.submit(download_tile, zoom, x, y)
                current_batch.append(task)
                downloaded += 1
                
                if len(current_batch) >= batch_size:
                    process_tile_batch(current_batch, max_retries)
                    current_batch = []
                    time.sleep(0.2)  # Rate limiting
                
                if downloaded % 20 == 0:  # More frequent progress updates
                    print(f"Progress: {downloaded}/{total_tiles} tiles ({(downloaded/total_tiles)*100:.1f}%)")
                    save_progress(zoom, x, y)
            
            # Process remaining tiles in the current row
            if current_batch:
                process_tile_batch(current_batch, max_retries)
            
            save_progress(zoom, x, 0)
            print(f"Completed row x={x}/{max_x}")

def get_last_completed_zoom() -> float:
    """Get the last completed zoom level from the downloaded files."""
    calculator = TileCalculator()
    zoom_levels = calculator.get_zoom_levels()
    completed = zoom_levels[0]  # Start from lowest zoom
    
    for zoom in zoom_levels:
        zoom_dir = OUTPUT_DIR / str(zoom)
        if zoom_dir.exists() and any(zoom_dir.iterdir()):
            completed = zoom
        else:
            break
    return completed

def verify_zoom_range(zoom: float) -> bool:
    """Verify that a zoom level is within the valid range."""
    return 12.4515 <= zoom <= 18.0000

def verify_coordinate_range(x: float, y: float, zoom: Optional[float] = None) -> bool:
    """Verify that coordinates are within the valid range for the given zoom level."""
    calculator = TileCalculator()
    
    # If no zoom provided, use the most restrictive range (base corners)
    if zoom is None:
        return (4079.86 <= x <= 156900.14) and (2793.01 <= y <= 14209.55)
    
    # Get tile range for this zoom level
    tile_range = calculator.get_tile_range(zoom)
    
    # Convert tile indices to world coordinates
    resolution = calculator._get_resolution_for_zoom(zoom)
    tile_size = 256  # OpenLayers default tile size
    
    # Calculate world coordinate bounds
    min_world_x = tile_range.min_x * tile_size * resolution + calculator.ORIGIN[0]
    max_world_x = (tile_range.max_x + 1) * tile_size * resolution + calculator.ORIGIN[0]
    # Y is inverted in tile coordinates
    max_world_y = -tile_range.min_y * tile_size * resolution + calculator.ORIGIN[1]
    min_world_y = -(tile_range.max_y + 1) * tile_size * resolution + calculator.ORIGIN[1]
    
    return (min_world_x <= x <= max_world_x) and (min_world_y <= y <= max_world_y)

def main():
    """Main function to download all tiles."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    zoom_levels = generate_zoom_levels()
    
    if not zoom_levels:
        print("Error: No valid zoom levels found in range 12.4515 to 18.0000")
        return
        
    print(f"Processing zoom levels from {zoom_levels[0]:.4f} to {zoom_levels[-1]:.4f}")
    last_completed = get_last_completed_zoom()
    
    # Find starting zoom level index
    start_index = 0
    for i, zoom in enumerate(zoom_levels):
        if zoom > last_completed:
            start_index = i
            break
    
    # Process remaining zoom levels
    total_zoom_levels = len(zoom_levels[start_index:])
    for i, zoom in enumerate(zoom_levels[start_index:], 1):
        print(f"\nProcessing zoom level {zoom:.4f} ({i}/{total_zoom_levels})")
        try:
            # Calculate size ratio before downloading
            calculator = TileCalculator()
            tile_range = calculator.get_tile_range(zoom)
            tile_size = 256  # OpenLayers default tile size
            final_width = (int(tile_range.max_x) - int(tile_range.min_x) + 1) * tile_size
            final_height = (int(tile_range.max_y) - int(tile_range.min_y) + 1) * tile_size
            base_width = 1976  # Original canvas width
            base_height = 2114  # Original canvas height
            size_ratio = (final_width * final_height) / (base_width * base_height)
            
            print(f"Size ratio at zoom {zoom:.4f}: {size_ratio:.2f}x")
            print(f"Final dimensions: {final_width}x{final_height}")
            
            if size_ratio < 10:
                print(f"Skipping zoom level {zoom:.4f} - output would be too small")
                continue
            elif size_ratio > 100:
                print(f"Skipping zoom level {zoom:.4f} - output would be too large")
                continue
                
            download_zoom_level(zoom)
            print(f"Completed zoom level {zoom:.4f}")
        except Exception as e:
            print(f"Error downloading zoom level {zoom:.4f}: {e}")
            # Continue with next zoom level even if one fails
            continue
        
    print("\nDownload process completed!")
    print("Verifying coverage...")
    
    # Verify coverage
    for zoom in zoom_levels:
        tile_range = get_tile_range(zoom)
        if not verify_coordinate_range(tile_range.min_x, tile_range.min_y, zoom) or \
           not verify_coordinate_range(tile_range.max_x, tile_range.max_y, zoom):
            print(f"Warning: Zoom level {zoom:.4f} may have incomplete coverage!")
            print(f"Range: ({tile_range.min_x}, {tile_range.min_y}) to ({tile_range.max_x}, {tile_range.max_y})")

if __name__ == "__main__":
    main()
