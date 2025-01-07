from PIL import Image
import os
import time
import psutil
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from tile_index_calculation import TileCalculator

# Constants
BASE_WIDTH = 1976
BASE_HEIGHT = 2114
TRANSFORM_MATRIX = (0.5, 0.0, 0.0, 0.5, 0.0, 0.0)
MIN_ZOOM = 12.4515
MAX_ZOOM = 18.0000

def ensure_output_directory(output_dir: str):
    """Ensure the output directory exists."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

def verify_coordinate_range(x: float, y: float, tolerance: float = 1.0) -> bool:
    """
    Verify that coordinates are within the valid range.
    
    Args:
        x: X coordinate (can be int or float)
        y: Y coordinate (can be int or float)
        tolerance: Allowed deviation from exact bounds (default: 1.0)
        
    Returns:
        bool: True if coordinates are within valid range (including tolerance)
    """
    X_MIN, X_MAX = 4079.86, 156900.14
    Y_MIN, Y_MAX = 2793.01, 14209.55
    
    # Convert to float and check ranges with tolerance
    x_float = float(x)
    y_float = float(y)
    
    return ((X_MIN - tolerance <= x_float <= X_MAX + tolerance) and 
            (Y_MIN - tolerance <= y_float <= Y_MAX + tolerance))

def verify_transform_matrix(x: float, y: float, width: int, height: int) -> bool:
    """
    Verify that coordinates after transform matrix are within canvas bounds.
    Takes into account the scale factor for output size requirements.
    """
    # Calculate scale factor based on output size requirements
    scale = (width * height) / (1976 * 2114)  # Base canvas size
    scale_factor = (scale ** 0.5) * 0.5  # Compensate for 0.5 transform
    
    # Apply transform with scaling
    transformed_x, transformed_y = apply_transform_matrix(
        x * scale_factor, y * scale_factor,
        (0.5, 0.0, 0.0, 0.5, 0.0, 0.0)
    )
    return 0 <= transformed_x <= width and 0 <= transformed_y <= height

def apply_transform_matrix(x: float, y: float, matrix: Tuple[float, float, float, float, float, float]) -> Tuple[float, float]:
    """Apply transform matrix to coordinates."""
    a, b, c, d, e, f = matrix
    new_x = a * x + c * y + e
    new_y = b * x + d * y + f
    return new_x, new_y

def calculate_pixel_position(x: float, y: float, zoom: float,
                           min_x: float, min_y: float,
                           canvas_width: int, canvas_height: int) -> Tuple[int, int]:
    """Calculate pixel position based on coordinates and zoom level."""
    # Normalize coordinates to canvas dimensions
    x_normalized = (x - min_x) / (156900.14 - 4079.86)  # Full x range
    y_normalized = (y - min_y) / (14209.55 - 2793.01)   # Full y range
    
    # Calculate base pixel positions
    pixel_x = int(x_normalized * canvas_width)
    pixel_y = int(y_normalized * canvas_height)
    
    # Apply transform matrix (0.5, 0, 0, 0.5, 0, 0)
    transformed_x, transformed_y = apply_transform_matrix(
        float(pixel_x), float(pixel_y),
        (0.5, 0.0, 0.0, 0.5, 0.0, 0.0)
    )
    
    return int(transformed_x), int(transformed_y)

def merge_tiles(base_dir: str, output_path: str, chunk_size: int = 4096) -> Tuple[Image.Image, bool]:
    """
    Merge downloaded tiles into a single large image using chunked processing.
    Returns:
        Tuple[Image.Image, bool]: The merged image and whether it meets size requirements
        
    Args:
        base_dir: Base directory containing tile images
        output_path: Path to save the merged image
        chunk_size: Size of chunks to process at a time (default: 4096)
    """
    print(f"\nStarting merge_tiles")
    print(f"Base directory: {base_dir}")
    print(f"Output path: {output_path}")
    
    # Initialize tile calculator
    calculator = TileCalculator()
    zoom_levels = [z for z in calculator.get_zoom_levels() 
                  if MIN_ZOOM <= z <= MAX_ZOOM]
    
    if not zoom_levels:
        raise ValueError(f"No valid zoom levels found in range {MIN_ZOOM} to {MAX_ZOOM}")
    
    print(f"Found {len(zoom_levels)} zoom levels to process")
    print(f"Zoom range: {min(zoom_levels):.4f} to {max(zoom_levels):.4f}")
    
    # Calculate output dimensions with transform matrix applied
    SCALE_FACTOR = 20  # For larger output (targeting middle of 10x-100x range)
    output_width = int(BASE_WIDTH * SCALE_FACTOR * 2)  # *2 to compensate for 0.5 transform
    output_height = int(BASE_HEIGHT * SCALE_FACTOR * 2)
    
    print(f"Output dimensions will be {output_width}x{output_height}")
    print(f"Processing in chunks of {chunk_size}x{chunk_size}")
    
    # Create base image with correct dimensions and transform matrix
    base_image = Image.new('RGBA', (output_width, output_height), (0, 0, 0, 0))
    
    # Create temporary directory for chunks
    temp_dir = Path(os.path.dirname(output_path)) / "temp_chunks"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Calculate number of chunks
    chunks_x = (output_width + chunk_size - 1) // chunk_size
    chunks_y = (output_height + chunk_size - 1) // chunk_size
    print(f"Will process in {chunks_x}x{chunks_y} chunks")
    
    # Track total tiles processed
    total_processed = 0
    total_tiles = 0
    
    try:
        start_time = time.time()
        
        # First count total tiles across all zoom levels
        print("Counting total tiles...")
        for zoom in sorted(zoom_levels):
            _, total = process_zoom_level(zoom, None, base_dir, count_only=True)
            total_tiles += total
        
        if total_tiles == 0:
            print("Warning: No tiles found to process")
            ensure_output_directory(os.path.dirname(output_path))
            base_image.save(output_path, 'PNG')
            return base_image, False
            
        print(f"Found {total_tiles} total tiles to process")
        
        # Now process tiles with progress tracking
        for zoom in sorted(zoom_levels):
            # Check timeout
            if time.time() - start_time > 300:  # 5 minute timeout
                raise TimeoutError("Merge operation exceeded 5 minutes")
                
            processed, _ = process_zoom_level(zoom, base_image, base_dir)
            total_processed += processed
            
            # Progress update with memory usage
            elapsed = time.time() - start_time
            memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            print(f"Progress: {total_processed}/{total_tiles} tiles ({(total_processed/total_tiles)*100:.1f}%)")
            print(f"Time elapsed: {elapsed:.1f}s, Memory usage: {memory_usage:.1f}MB")
            
    except TimeoutError as e:
        print(f"Timeout error: {str(e)}")
        return base_image, False
    except Exception as e:
        print(f"Error during merge: {str(e)}")
        return base_image, False
    
    print(f"\nProcessed {total_processed}/{total_tiles} tiles ({(total_processed/total_tiles)*100:.1f}%)")
    
    # Initialize tracking variables
    total_processed = 0
    total_tiles = 0
    
    try:
        # First count total tiles
        print("\nCounting total tiles...")
        for zoom in sorted(zoom_levels):
            processed, total = process_zoom_level(zoom, None, base_dir, count_only=True)
            total_tiles += total
            
        if total_tiles == 0:
            print("Warning: No tiles found to process")
            empty_image = Image.new('RGBA', (output_width, output_height), (255, 255, 255, 0))
            return empty_image, False
            
        print(f"Found {total_tiles} total tiles to process")
        
        # Process chunks
        for chunk_y in range(chunks_y):
            for chunk_x in range(chunks_x):
                # Calculate chunk boundaries
                x_start = chunk_x * chunk_size
                y_start = chunk_y * chunk_size
                x_end = min(x_start + chunk_size, output_width)
                y_end = min(y_start + chunk_size, output_height)
                
                # Create chunk image
                chunk_image = Image.new('RGBA', (x_end - x_start, y_end - y_start), (255, 255, 255, 0))
                chunk_path = temp_dir / f"chunk_{chunk_x}_{chunk_y}.png"
                
                print(f"Processing chunk ({chunk_x+1}/{chunks_x}, {chunk_y+1}/{chunks_y})")
                
                # Process tiles for this chunk
                for zoom in sorted(zoom_levels):
                    processed = process_chunk(zoom, chunk_image, base_dir, x_start, y_start, x_end, y_end)
                    total_processed += processed
                    
                    # Progress update
                    print(f"Progress: {total_processed}/{total_tiles} tiles ({(total_processed/total_tiles)*100:.1f}%)")
                    print(f"Memory usage: {psutil.Process().memory_info().rss / 1024 / 1024:.1f}MB")
                
                # Save chunk
                chunk_image.save(chunk_path, 'PNG')
                chunk_image.close()
                
        # Combine chunks into final image
        print("\nCombining chunks into final image...")
        ensure_output_directory(os.path.dirname(output_path))
        
        final_image = Image.new('RGBA', (output_width, output_height), (255, 255, 255, 0))
        for chunk_y in range(chunks_y):
            for chunk_x in range(chunks_x):
                chunk_path = temp_dir / f"chunk_{chunk_x}_{chunk_y}.png"
                if chunk_path.exists():
                    with Image.open(chunk_path) as chunk:
                        x_start = chunk_x * chunk_size
                        y_start = chunk_y * chunk_size
                        final_image.paste(chunk, (x_start, y_start))
        
        final_image.save(output_path, 'PNG')
    
        # Clean up temporary chunks
        shutil.rmtree(temp_dir)
        
        # Verify final size requirements
        output_size = os.path.getsize(output_path)
        base_size = BASE_WIDTH * BASE_HEIGHT
        
    except Exception as e:
        print(f"Error during merge: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        empty_image = Image.new('RGBA', (output_width, output_height), (255, 255, 255, 0))
        return empty_image, False
    size_ratio = output_size / base_size
    print(f"Output size ratio: {size_ratio:.2f}x")
    
    meets_requirements = 10 <= size_ratio <= 100
    if not meets_requirements:
        print(f"Warning: Output size ratio {size_ratio:.2f}x is outside target range (10x-100x)")
    
    return final_image, meets_requirements

def process_chunk(zoom: float, chunk_image: Image.Image, base_dir: str,
                x_start: int, y_start: int, x_end: int, y_end: int) -> int:
    """Process tiles for a specific chunk of the output image."""
    zoom_str = f"{zoom:.4f}"
    zoom_dir = os.path.join(base_dir, zoom_str)
    
    if not os.path.exists(zoom_dir):
        return 0
        
    processed_tiles = 0
        
    # Process tiles that intersect with this chunk
    for x_dir in os.listdir(zoom_dir):
        x_path = os.path.join(zoom_dir, x_dir)
        if not os.path.isdir(x_path):
            continue
            
        try:
            x = int(x_dir)
            
            for y_file in os.listdir(x_path):
                if not y_file.endswith('.png'):
                    continue
                    
                try:
                    y = int(y_file.replace('.png', ''))
                    
                    # Verify coordinates are in range
                    if not verify_coordinate_range(float(x), float(y)):
                        continue
                    
                    # Calculate pixel position
                    pixel_x, pixel_y = calculate_pixel_position(
                        float(x), float(y), zoom,
                        4079.86, 2793.01,
                        chunk_image.width, chunk_image.height
                    )
                    
                    # Check if tile intersects with chunk
                    if (x_start <= pixel_x < x_end and 
                        y_start <= pixel_y < y_end):
                        
                        tile_path = os.path.join(x_path, y_file)
                        tile = Image.open(tile_path)
                        
                        if tile.mode != 'RGBA':
                            tile = tile.convert('RGBA')
                            
                        # Adjust coordinates for chunk
                        chunk_x = pixel_x - x_start
                        chunk_y = pixel_y - y_start
                        chunk_image.paste(tile, (chunk_x, chunk_y), tile)
                        tile.close()
                        processed_tiles += 1
                        
                except Exception as e:
                    print(f"Error processing tile: {str(e)}")
                    continue
                    
        except ValueError:
            continue
            
    return processed_tiles

def process_zoom_level(zoom: float, base_image: Optional[Image.Image], base_dir: str, count_only: bool = False) -> Tuple[int, int]:
    """Process all tiles for a specific zoom level. Returns (processed_tiles, total_tiles)."""
    print(f"\nProcessing zoom level {zoom:.4f}")
    zoom_str = f"{zoom:.4f}"
    zoom_dir = os.path.join(base_dir, zoom_str)
    
    if not os.path.exists(zoom_dir):
        print(f"Warning: Directory not found for zoom level {zoom_str}")
        return (0, 0)
        
    print(f"Found zoom directory: {zoom_dir}")
    
    # Only verify canvas dimensions if we're not in count_only mode
    if not count_only and base_image is not None:
        width, height = base_image.size
        if not verify_transform_matrix(width, height, width, height):
            print(f"Warning: Canvas dimensions {width}x{height} may be incorrect after transform")
    
    print(f"\nProcessing zoom level {zoom_str}")
    
    # First count total tiles
    total_tiles = 0
    processed_tiles = 0
    
    try:
        for x_dir in os.listdir(zoom_dir):
            x_path = os.path.join(zoom_dir, x_dir)
            if not os.path.isdir(x_path):
                continue
            for y_file in os.listdir(x_path):
                if y_file.endswith('.png'):
                    total_tiles += 1
    except Exception as e:
        print(f"Error counting tiles in {zoom_dir}: {str(e)}")
        return (0, 0)
        
    if total_tiles == 0:
        print(f"No tiles found in {zoom_dir}")
        return (0, 0)
        
    print(f"Found {total_tiles} tiles to process")
    
    # Now process tiles
    for x_dir in os.listdir(zoom_dir):
        x_path = os.path.join(zoom_dir, x_dir)
        if not os.path.isdir(x_path):
            continue
            
        try:
            x = int(x_dir)
            
            for y_file in os.listdir(x_path):
                if not y_file.endswith('.png'):
                    continue
                    
                try:
                    y = int(y_file.replace('.png', ''))
                    tile_path = os.path.join(x_path, y_file)
                    
                    # Verify coordinates are in range
                    if not verify_coordinate_range(float(x), float(y)):
                        print(f"Warning: Coordinates ({x}, {y}) out of range, skipping")
                        continue
                    
                    if count_only:
                        total_tiles += 1
                        continue
                        
                    if base_image is None:
                        print(f"Error: base_image is None but count_only is False")
                        continue
                        
                    tile = Image.open(tile_path)
                    pixel_x, pixel_y = calculate_pixel_position(
                        float(x), float(y), zoom,
                        4079.86, 2793.01,
                        base_image.width, base_image.height
                    )
                    
                    if tile.mode != 'RGBA':
                        tile = tile.convert('RGBA')
                        
                    base_image.paste(tile, (pixel_x, pixel_y), tile)
                    processed_tiles += 1
                    
                    if processed_tiles % 100 == 0:
                        print(f"Progress: {processed_tiles}/{total_tiles} tiles ({(processed_tiles/total_tiles)*100:.1f}%)")
                        
                except Exception as e:
                    print(f"Error processing tile {tile_path}: {str(e)}")
                    continue
                    
        except ValueError as e:
            print(f"Error parsing directory {x_dir}: {str(e)}")
            continue
            
    print(f"Completed zoom level {zoom_str}: processed {processed_tiles}/{total_tiles} tiles")
    return (processed_tiles, total_tiles)

if __name__ == '__main__':
    base_dir = 'downloaded_tiles'
    output_path = 'merged_visualization.png'
    
    # Process all zoom levels
    calculator = TileCalculator()
    zoom_levels = [z for z in calculator.get_zoom_levels() 
                  if 12.4515 <= z <= 18.0000]
                  
    if not zoom_levels:
        print("No valid zoom levels found")
        exit(1)
        
    print(f"Found {len(zoom_levels)} zoom levels to process")
    print(f"Zoom range: {min(zoom_levels):.4f} to {max(zoom_levels):.4f}")
    
    # Create and process base image
    merged = merge_tiles(base_dir, output_path)
    
    # Verify size requirements based on pixel dimensions
    output_image = Image.open(output_path)
    output_pixels = output_image.size[0] * output_image.size[1]
    base_pixels = 1976 * 2114  # Original canvas size
    size_ratio = output_pixels / base_pixels
    
    print(f"\nOutput size ratio: {size_ratio:.2f}x")
    if 10 <= size_ratio <= 100:
        print("Successfully merged visualization with required size ratio")
    else:
        print("Warning: Output size does not meet 10x-100x requirement")
