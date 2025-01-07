#!/usr/bin/env python3

import unittest
from tile_index_calculation import TileCalculator, TileIndex, Bounds

class TestTileCalculator(unittest.TestCase):
    def setUp(self):
        self.calculator = TileCalculator()

    def test_zoom_levels(self):
        """Test that zoom levels are generated correctly."""
        levels = self.calculator.get_zoom_levels()
        self.assertTrue(12.4515 <= levels[0] <= 12.4516)  # First level
        self.assertTrue(17.9999 <= levels[-1] <= 18.0001)  # Last level
        
        # Test increment
        for i in range(len(levels) - 1):
            diff = levels[i + 1] - levels[i]
            self.assertAlmostEqual(diff, 0.66, places=2)

    def test_tile_range(self):
        """Test tile range calculation for a specific zoom level."""
        tile_range = self.calculator.get_tile_range(14.8544)
        
        # Ensure we get valid tile indices
        self.assertIsInstance(tile_range['min_x'], int)
        self.assertIsInstance(tile_range['max_x'], int)
        self.assertIsInstance(tile_range['min_y'], int)
        self.assertIsInstance(tile_range['max_y'], int)
        
        # Ensure ranges make sense
        self.assertTrue(tile_range['min_x'] < tile_range['max_x'])
        self.assertTrue(tile_range['min_y'] < tile_range['max_y'])

    def test_coordinate_conversion(self):
        """Test coordinate to tile conversion."""
        # Test with known corner coordinates
        tile = self.calculator._coordinates_to_tile(4079.86, 14209.55, 14)
        self.assertIsInstance(tile, TileIndex)
        self.assertEqual(tile.zoom, 14)

if __name__ == '__main__':
    unittest.main()
