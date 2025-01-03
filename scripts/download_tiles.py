import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

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

def download_zoom_level(zoom: int):
    """Download all tiles for a specific zoom level."""
    # Start with a small range and expand based on successful downloads
    x_range = range(0, 20)
    y_range = range(0, 20)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        for x in x_range:
            for y in y_range:
                executor.submit(download_tile, zoom, x, y)
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)

def main():
    """Main function to download all tiles."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Start with zoom levels we observed in the console (around 7)
    # and explore nearby levels
    zoom_levels = range(5, 15)
    
    for zoom in zoom_levels:
        print(f"Downloading zoom level {zoom}")
        download_zoom_level(zoom)

if __name__ == "__main__":
    main()
