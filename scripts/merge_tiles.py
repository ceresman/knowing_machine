#!/usr/bin/env python3
"""
Merge downloaded tiles into complete images for each zoom level.
"""
import os
from pathlib import Path
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TileMerger:
    def __init__(self, tiles_dir: str | Path, output_dir: str | Path):
        """Initialize the TileMerger with input and output directories."""
        self.tiles_dir = Path(tiles_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def merge_zoom_level(self, zoom_level: int) -> Path:
        """Merge all tiles for a specific zoom level into a single image."""
        zoom_dir = self.tiles_dir / str(zoom_level)
        if not zoom_dir.exists():
            raise ValueError(f"Zoom level {zoom_level} directory not found")
            
        # Get grid dimensions
        x_coords = sorted([int(x.name) for x in zoom_dir.iterdir()])
        y_coords = []
        for x_dir in zoom_dir.iterdir():
            y_coords.extend([int(y.stem) for y in x_dir.iterdir()])
        y_coords = sorted(set(y_coords))
        
        # Calculate final image dimensions
        tile_width = tile_height = 512  # Known tile dimensions
        total_width = len(x_coords) * tile_width
        total_height = len(y_coords) * tile_height
        
        # Create new image with the calculated dimensions
        merged_image = Image.new('RGBA', (total_width, total_height))
        
        # Merge tiles
        for x_idx, x in enumerate(x_coords):
            for y_idx, y in enumerate(y_coords):
                tile_path = zoom_dir / str(x) / f"{y}.png"
                if tile_path.exists():
                    try:
                        with Image.open(tile_path) as tile:
                            merged_image.paste(
                                tile,
                                (x_idx * tile_width, y_idx * tile_height)
                            )
                    except Exception as e:
                        logger.error(f"Error processing tile {tile_path}: {e}")
                else:
                    logger.warning(f"Missing tile at {tile_path}")
        
        # Save merged image
        output_path = self.output_dir / f"merged_zoom_{zoom_level}.png"
        merged_image.save(output_path, "PNG", optimize=True)
        logger.info(f"Saved merged image for zoom level {zoom_level} to {output_path}")
        return output_path

    def merge_all_zoom_levels(self) -> dict:
        """Merge tiles for all available zoom levels."""
        merged_images = {}
        zoom_levels = sorted([
            int(d.name) for d in self.tiles_dir.iterdir() if d.is_dir()
        ])
        
        for zoom in zoom_levels:
            try:
                output_path = self.merge_zoom_level(zoom)
                merged_images[zoom] = output_path
                logger.info(f"Successfully merged zoom level {zoom}")
            except Exception as e:
                logger.error(f"Failed to merge zoom level {zoom}: {e}")
        
        return merged_images

def main():
    """Main entry point for the tile merger script."""
    script_dir = Path(__file__).parent
    tiles_dir = script_dir / "downloaded_tiles"
    output_dir = script_dir / "merged_tiles"
    
    merger = TileMerger(tiles_dir, output_dir)
    try:
        merged_images = merger.merge_all_zoom_levels()
        logger.info("Merged images saved to:")
        for zoom, path in merged_images.items():
            logger.info(f"Zoom level {zoom}: {path}")
    except Exception as e:
        logger.error(f"Error merging tiles: {e}")
        raise

if __name__ == "__main__":
    main()
