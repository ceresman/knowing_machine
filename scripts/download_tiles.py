import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor, Future
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Tuple

@dataclass
class TileTask:
    zoom: int
    x: int
    y: int
    future: Optional[Future] = None
    success: bool = False

BASE_URL = "https://tiles.calculatingempires.net/tiles_directory_black_10"
OUTPUT_DIR = Path("downloaded_tiles")

def download_tile(zoom: int, x: int, y: int) -> bool:
    """Download a single tile and save it to the appropriate directory."""
    url = f"{BASE_URL}/{zoom}/{x}/{y}.png"
    output_path = OUTPUT_DIR / str(zoom) / str(x)
    output_file = output_path / f"{y}.png"
    
    if output_file.exists():
        return True
    
    try:
        response = requests.get(url)
        if response.status_code == 404:
            return False
        
        output_path.mkdir(parents=True, exist_ok=True)
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Downloaded tile: zoom={zoom}, x={x}, y={y}")
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def calculate_tile_range(zoom: int) -> tuple[range, range]:
    """Calculate the x,y ranges for a given zoom level."""
    # Each zoom level doubles the number of tiles in each dimension
    size = 2 ** (zoom - 5)  # Using zoom 5 as base
    return range(0, size * 20), range(0, size * 20)

def get_progress_file(zoom: int) -> Path:
    """Get the progress file path for a zoom level."""
    return OUTPUT_DIR / f"progress_{zoom}.txt"

def save_progress(zoom: int, x: int, y: int):
    """Save the current progress for a zoom level."""
    with open(get_progress_file(zoom), 'w') as f:
        f.write(f"{x},{y}")

def load_progress(zoom: int) -> tuple[int, int]:
    """Load the progress for a zoom level."""
    progress_file = get_progress_file(zoom)
    if progress_file.exists():
        with open(progress_file) as f:
            x, y = map(int, f.read().strip().split(','))
            return x, y
    return 0, 0

def check_tile_exists(zoom: int, x: int, y: int) -> bool:
    """Check if a tile exists at the given coordinates."""
    url = f"{BASE_URL}/{zoom}/{x}/{y}.png"
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

def download_zoom_level(zoom: int):
    """Download all tiles for a specific zoom level."""
    x_range, y_range = calculate_tile_range(zoom)
    max_retries = 3
    start_x, start_y = load_progress(zoom)
    
    # First, check the boundaries of valid tiles
    print(f"Checking boundaries for zoom level {zoom}...")
    max_x = max_y = -1  # Start at -1 to handle case where no tiles exist
    
    # Binary search for max_x and max_y to speed up boundary detection
    def binary_search_max(coord_type: str, max_range: int) -> int:
        left, right = 0, max_range - 1
        while left <= right:
            mid = (left + right) // 2
            exists = check_tile_exists(zoom, mid if coord_type == 'x' else 0, 
                                    0 if coord_type == 'x' else mid)
            if exists:
                left = mid + 1
            else:
                right = mid - 1
        return right
    
    max_x = binary_search_max('x', len(x_range))
    max_y = binary_search_max('y', len(y_range))
    
    if max_x < 0 or max_y < 0:
        print(f"No valid tiles found for zoom level {zoom}")
        return
    
    total_tiles = (max_x + 1) * (max_y + 1)
    downloaded = 0
    
    print(f"Starting zoom level {zoom} from position x={start_x}, y={start_y}")
    print(f"Valid tile range: x=0-{max_x}, y=0-{max_y}")
    print(f"Total tiles to process: {total_tiles}")
    
    batch_size = 4
    with ThreadPoolExecutor(max_workers=4) as executor:
        for x in range(start_x, max_x + 1):
            y_start = start_y if x == start_x else 0
            current_batch: List[TileTask] = []
            
            for y in range(y_start, max_y + 1):
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

def get_last_completed_zoom() -> int:
    """Get the last completed zoom level from the downloaded files."""
    completed = 4  # Start from zoom level 4
    for zoom in range(5, 16):
        zoom_dir = OUTPUT_DIR / str(zoom)
        if zoom_dir.exists() and any(zoom_dir.iterdir()):
            completed = zoom
        else:
            break
    return completed

def main():
    """Main function to download all tiles."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Resume from the last completed zoom level
    start_zoom = get_last_completed_zoom() + 1
    zoom_levels = range(start_zoom, 16)  # Include zoom level 15
    
    for zoom in zoom_levels:
        print(f"Downloading zoom level {zoom}")
        try:
            download_zoom_level(zoom)
            print(f"Completed zoom level {zoom}")
        except Exception as e:
            print(f"Error downloading zoom level {zoom}: {e}")
            # Continue with next zoom level even if one fails
            continue

if __name__ == "__main__":
    main()
