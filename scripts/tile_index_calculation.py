#!/usr/bin/env python3

import math
from typing import Tuple, List, Dict
from dataclasses import dataclass

@dataclass
class Bounds:
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_zoom: float
    max_zoom: float

@dataclass
class TileIndex:
    x: int
    y: int
    zoom: int

class TileCalculator:
    # OpenLayers TileGrid configuration from webpage
    RESOLUTIONS = [
        1024.01272239340028, 512.006361196700141, 256.00318059835007,
        128.001590299175035, 64.0007951495875176, 32.0003975747937588,
        16.0001987873968794, 8.0000993936984397, 4.00004969684921985,
        2.00002484842460992, 1.00001242421230496
    ]
    
    # TileGrid extent and origin from webpage
    EXTENT = [0, 0.779308716828381876, 160980.000024848414, 17764]
    ORIGIN = [0, 0.779308716828381876]
    
    def __init__(self):
        # Map resolutions to zoom levels (0-based index)
        self.resolution_to_zoom = {res: i for i, res in enumerate(self.RESOLUTIONS)}
        self.zoom_to_resolution = {i: res for i, res in enumerate(self.RESOLUTIONS)}
        
        # Initialize bounds to handle both TileGrid extent and user-provided corners
        self.bounds = Bounds(
            min_x=min(self.EXTENT[0], 4079.86),
            max_x=max(self.EXTENT[2], 156900.14),
            min_y=min(self.EXTENT[1], 2793.01),
            max_y=max(self.EXTENT[3], 14209.55),
            min_zoom=12.4515,  # From center-and-zoom.js constraints
            max_zoom=18.0000
        )
        
        # Canvas properties from webpage
        self.canvas_width = 1976
        self.canvas_height = 2114
        self.transform_scale = 0.5  # From matrix(0.5, 0, 0, 0.5, 0, 0)
        self.tile_size = 256  # From TileGrid configuration

    def _get_resolution_for_zoom(self, zoom: float) -> float:
        """Get resolution for a given zoom level using OpenLayers resolution array."""
        # Map zoom level to resolution index (inverted)
        # zoom 12.4515 (min) -> index 0 -> max resolution (1024.01...)
        # zoom 18.0000 (max) -> index -1 -> min resolution (1.00...)
        normalized = 1.0 - ((zoom - 12.4515) / (18.0000 - 12.4515))  # 1 to 0
        index = int(round(normalized * (len(self.RESOLUTIONS) - 1)))
        index = max(0, min(len(self.RESOLUTIONS) - 1, index))
        return self.RESOLUTIONS[index]

    def _coordinates_to_tile(self, x: float, y: float, zoom: float) -> TileIndex:
        """Convert world coordinates to tile indices using OpenLayers resolution."""
        resolution = self._get_resolution_for_zoom(zoom)
        
        # Calculate tile coordinates using OpenLayers convention
        # X increases from left to right
        tile_x = math.floor((x - self.ORIGIN[0]) / (resolution * self.tile_size))
        
        # Y is inverted in OpenLayers - convert from world coordinates to tile coordinates
        # First, get Y distance from origin in world coordinates
        y_dist = y - self.ORIGIN[1]
        # Convert to pixels
        y_pixels = y_dist / resolution
        # Convert to tile index (negative because OpenLayers uses negative Y indices)
        tile_y = -1 - math.floor(y_pixels / self.tile_size)
        
        # Calculate zoom index (0 to 10) for OpenLayers zoom levels
        normalized = (zoom - self.bounds.min_zoom) / (self.bounds.max_zoom - self.bounds.min_zoom)
        ol_zoom = int(round(normalized * (len(self.RESOLUTIONS) - 1)))
        ol_zoom = max(0, min(len(self.RESOLUTIONS) - 1, ol_zoom))
        
        # Ensure tile indices are within valid range
        max_tile = 2 ** ol_zoom - 1
        tile_x = max(0, min(tile_x, max_tile))
        tile_y = max(-max_tile - 1, min(tile_y, -1))
        
        return TileIndex(tile_x, tile_y, ol_zoom)

    def get_zoom_levels(self) -> List[float]:
        """Get all valid zoom levels matching OpenLayers resolutions."""
        zoom_levels = []
        current = self.bounds.min_zoom
        
        while current <= self.bounds.max_zoom:
            zoom_levels.append(round(current, 4))
            # Use 0.66 increment as observed from webpage
            current = round(current + 0.66, 4)
        
        # Ensure max zoom is included
        if zoom_levels[-1] != self.bounds.max_zoom:
            zoom_levels.append(self.bounds.max_zoom)
            
        return zoom_levels
        
    def get_resolution_for_tile(self, zoom: float) -> float:
        """Get the resolution for a specific zoom level."""
        return self._get_resolution_for_zoom(zoom)
        
    def verify_coordinate_coverage(self, x: float, y: float, zoom: float) -> Dict:
        """Verify that coordinates are within bounds at given zoom level."""
        resolution = self._get_resolution_for_zoom(zoom)
        tile = self._coordinates_to_tile(x, y, zoom)
        
        # Calculate world coordinates in pixels at this resolution
        px = (x - self.ORIGIN[0]) / resolution
        py = (y - self.ORIGIN[1]) / resolution
        
        # Calculate viewport dimensions in world pixels
        viewport_width = self.canvas_width / self.transform_scale
        viewport_height = self.canvas_height / self.transform_scale
        
        # Calculate tile grid coverage based on resolution
        tiles_x = math.ceil(viewport_width / (self.tile_size * resolution))
        tiles_y = math.ceil(viewport_height / (self.tile_size * resolution))
        total_tiles = tiles_x * tiles_y
        
        # Calculate final image dimensions
        final_width = tiles_x * self.tile_size
        final_height = tiles_y * self.tile_size
        
        # Calculate size ratio relative to canvas
        # Account for both transform scale and resolution
        base_area = self.canvas_width * self.canvas_height
        final_area = final_width * final_height / (resolution * resolution)
        size_ratio = final_area / base_area
        
        # Check if coordinates are within TileGrid extent
        in_bounds = (
            self.EXTENT[0] <= x <= self.EXTENT[2] and
            self.EXTENT[1] <= y <= self.EXTENT[3]
        )
        
        return {
            "in_bounds": in_bounds,
            "pixel_coords": (px, py),
            "viewport_size": (viewport_width, viewport_height),
            "tile_coords": (tile.x, tile.y),
            "resolution": resolution,
            "tiles_required": total_tiles,
            "size_ratio": size_ratio,
            "final_dimensions": (final_width, final_height)
        }

    def get_tile_range(self, zoom: float) -> Bounds:
        """Get the range of tiles needed for a specific zoom level."""
        resolution = self._get_resolution_for_zoom(zoom)
        
        # Calculate normalized zoom level (0 to 10)
        normalized = (zoom - self.bounds.min_zoom) / (self.bounds.max_zoom - self.bounds.min_zoom)
        ol_zoom = int(round(normalized * (len(self.RESOLUTIONS) - 1)))
        ol_zoom = max(0, min(len(self.RESOLUTIONS) - 1, ol_zoom))
        
        # Maximum tile index at this zoom level
        max_tile = 2 ** ol_zoom - 1
        
        # Get corner tiles for both TileGrid extent and user-provided corners
        corners = [
            (self.EXTENT[0], self.EXTENT[3]),  # TileGrid top-left
            (self.EXTENT[2], self.EXTENT[1]),  # TileGrid bottom-right
            (4079.86, 14209.55),               # User top-left
            (156900.14, 2793.01)               # User bottom-right
        ]
        
        # Calculate tile indices for all corners with bounds checking
        tile_indices = []
        for x, y in corners:
            tile = self._coordinates_to_tile(x, y, zoom)
            # Ensure tile indices are within valid range
            tile_x = max(0, min(tile.x, max_tile))
            tile_y = max(-max_tile - 1, min(tile.y, -1))
            tile_indices.append(TileIndex(tile_x, tile_y, ol_zoom))
        
        # Find the extreme tile coordinates
        min_tile_x = max(0, min(tile.x for tile in tile_indices))
        max_tile_x = min(max_tile, max(tile.x for tile in tile_indices))
        min_tile_y = max(-max_tile - 1, min(tile.y for tile in tile_indices))
        max_tile_y = min(-1, max(tile.y for tile in tile_indices))
        
        return Bounds(
            min_x=float(min_tile_x),
            max_x=float(max_tile_x),
            min_y=float(min_tile_y),
            max_y=float(max_tile_y),
            min_zoom=zoom,
            max_zoom=zoom
        )

    def calculate_all_tiles(self) -> List[Bounds]:
        """Calculate all required tiles across all zoom levels."""
        all_tiles = []
        for zoom in self.get_zoom_levels():
            tile_range = self.get_tile_range(zoom)
            all_tiles.append(tile_range)
        return all_tiles

def main():
    calculator = TileCalculator()
    
    # Test coordinates from user requirements
    test_coords = [
        (4079.86, 14209.55, 14.8544),    # leftup
        (156900.14, 2793.01, 14.8544),   # rightdown
        (93000.24, 8725.00, 12.5511),    # min zoom example
        (92988.96, 8777.58, 18.0000)     # max zoom example
    ]
    
    # Verify coordinate coverage
    print("Verifying coordinate coverage...")
    for x, y, z in test_coords:
        coverage = calculator.verify_coordinate_coverage(x, y, z)
        print(f"\nCoordinate ({x}, {y}) at zoom {z}:")
        print(f"In bounds: {coverage['in_bounds']}")
        print(f"Pixel coordinates: {coverage['pixel_coords']}")
        print(f"Tile coordinates: {coverage['tile_coords']}")
        print(f"Resolution: {coverage['resolution']}")
        print(f"Tiles required: {coverage['tiles_required']}")
    
    # Calculate and print tile ranges for key zoom levels
    print("\nCalculating tile ranges for key zoom levels...")
    key_zooms = [12.4515, 14.8544, 18.0000]  # min, example, max
    
    for zoom in key_zooms:
        tile_range = calculator.get_tile_range(zoom)
        width = int(tile_range.max_x - tile_range.min_x + 1)
        height = int(tile_range.max_y - tile_range.min_y + 1)
        total_tiles = width * height
        resolution = calculator._get_resolution_for_zoom(zoom)
        
        print(f"\nZoom level {zoom:.4f} (resolution: {resolution:.6f}):")
        print(f"X range: {tile_range.min_x:.2f} to {tile_range.max_x:.2f}")
        print(f"Y range: {tile_range.min_y:.2f} to {tile_range.max_y:.2f}")
        print(f"Grid size: {width}x{height} ({total_tiles} tiles)")
        
        # Calculate final image size at this zoom
        img_width = width * calculator.tile_size
        img_height = height * calculator.tile_size
        size_ratio = (img_width * img_height) / (calculator.canvas_width * calculator.canvas_height)
        
        print(f"Final image size: {img_width}x{img_height} (ratio to canvas: {size_ratio:.2f}x)")

if __name__ == "__main__":
    main()
