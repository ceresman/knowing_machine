import os
import math
import requests
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://tiles.calculatingempires.net/tiles_directory_black_10"
MIN_ZOOM = 12
MAX_ZOOM = 18
ZOOM_LEVELS = [12, 13, 14, 15, 16, 17, 18]  # Integer zoom levels
LEFT_UP_POS = (4079.86, 14209.55)
RIGHT_DOWN_POS = (156900.14, 2793.01)

# Create output directory
OUTPUT_DIR = Path("downloaded_tiles")
OUTPUT_DIR.mkdir(exist_ok=True)

def calculate_tile_indices(zoom_level):
    """Calculate tile indices for a given zoom level."""
    tile_size = 256  # Standard tile size
    scale = 2 ** zoom_level
    
    # Convert coordinates to tile indices with bounds checking
    left_tile = max(0, math.floor(LEFT_UP_POS[0] / tile_size * scale))
    right_tile = max(0, math.ceil(RIGHT_DOWN_POS[0] / tile_size * scale))
    top_tile = max(0, math.floor(LEFT_UP_POS[1] / tile_size * scale))
    bottom_tile = max(0, math.ceil(RIGHT_DOWN_POS[1] / tile_size * scale))
    
    # Ensure valid tile ranges
    max_tile = 2 ** zoom_level - 1
    right_tile = min(right_tile, max_tile)
    bottom_tile = min(bottom_tile, max_tile)
    
    return left_tile, right_tile, top_tile, bottom_tile

def download_tile(zoom, x, y, retries=3, delay=1):
    """Download a single tile with retries."""
    url = f"{BASE_URL}/{zoom}/{x}/{y}.png"
    output_dir = OUTPUT_DIR / str(zoom) / str(x)
    output_file = output_dir / f"{y}.png"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200: 
                output_file.write_bytes(response.content)
                return True
            elif response.status_code == 404:
                logger.debug(f"Tile not found: {url}")
                return False
            else:
                logger.warning(f"Failed to download tile: {url} (Status: {response.status_code})")
                if attempt < retries - 1:
                    time.sleep(delay)
                    continue
        except Exception as e:
            logger.error(f"Error downloading tile {url}: {str(e)}")
            if attempt < retries - 1:
                time.sleep(delay)
                continue
    return False

def download_zoom_level(zoom_level):
    """Download all tiles for a specific zoom level."""
    left, right, top, bottom = calculate_tile_indices(zoom_level)
    total_tiles = (right - left + 1) * (bottom - top + 1)
    downloaded = 0
    failed = 0
    
    logger.info(f"Downloading zoom level {zoom_level} ({total_tiles} tiles)")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                futures.append(executor.submit(download_tile, zoom_level, x, y))
        
        for future in as_completed(futures):
            if future.result():
                downloaded += 1
            else:
                failed += 1
            
            if (downloaded + failed) % 100 == 0:
                logger.info(f"Progress: {downloaded + failed}/{total_tiles} ({downloaded} success, {failed} failed)")
    
    return downloaded, failed

def main():
    """Main function to download all tiles."""
    logger.info("Starting full visualization download")
    start_time = time.time()
    
    total_downloaded = 0
    total_failed = 0
    
    for zoom in ZOOM_LEVELS:
        try:
            logger.info(f"Processing zoom level {zoom}")
            downloaded, failed = download_zoom_level(zoom)
            total_downloaded += downloaded
            total_failed += failed
            
            elapsed = time.time() - start_time
            logger.info(f"Completed zoom level {zoom}: {downloaded} downloaded, {failed} failed")
            logger.info(f"Elapsed time: {elapsed:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error processing zoom level {zoom}: {str(e)}")
            continue
    
    logger.info(f"Download complete. Total: {total_downloaded} success, {total_failed} failed")
    logger.info(f"Total elapsed time: {time.time() - start_time:.2f} seconds")
    
    logger.info(f"Download complete. Total: {total_downloaded} success, {total_failed} failed")

if __name__ == "__main__":
    main()
