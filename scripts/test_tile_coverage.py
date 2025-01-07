import unittest
from download_tiles import verify_zoom_range, verify_coordinate_range
from tile_index_calculation import TileCalculator

class TestTileCoverage(unittest.TestCase):
    def setUp(self):
        self.calculator = TileCalculator()
    
    def test_zoom_range(self):
        """Test zoom level validation."""
        self.assertTrue(verify_zoom_range(12.4515))
        self.assertTrue(verify_zoom_range(18.0000))
        self.assertTrue(verify_zoom_range(14.8544))
        self.assertFalse(verify_zoom_range(12.0000))
        self.assertFalse(verify_zoom_range(19.0000))
    
    def test_coordinate_range(self):
        """Test coordinate range validation."""
        # Test leftup corner
        self.assertTrue(verify_coordinate_range(4079.86, 14209.55))
        # Test rightdown corner
        self.assertTrue(verify_coordinate_range(156900.14, 2793.01))
        # Test out of bounds
        self.assertFalse(verify_coordinate_range(0, 0))
        self.assertFalse(verify_coordinate_range(200000, 20000))
    
    def test_tile_calculator_coverage(self):
        """Test that TileCalculator covers the required ranges."""
        zoom_levels = self.calculator.get_zoom_levels()
        self.assertTrue(any(abs(z - 12.4515) < 0.0001 for z in zoom_levels), "Missing min zoom")
        self.assertTrue(any(abs(z - 18.0000) < 0.0001 for z in zoom_levels), "Missing max zoom")
        
        # Test specific zoom level coverage
        test_zoom = 14.8544
        tile_range = self.calculator.get_tile_range(test_zoom)
        self.assertTrue(verify_coordinate_range(tile_range.min_x, tile_range.min_y))
        self.assertTrue(verify_coordinate_range(tile_range.max_x, tile_range.max_y))

if __name__ == '__main__':
    unittest.main()
