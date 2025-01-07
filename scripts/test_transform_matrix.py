import unittest
import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from merge_visualization import (
    apply_transform_matrix,
    verify_transform_matrix,
    verify_coordinate_range
)

class TestTransformMatrix(unittest.TestCase):
    def test_transform_matrix(self):
        """Test transform matrix application."""
        # Test basic transformation
        x, y = apply_transform_matrix(100.0, 200.0, (0.5, 0.0, 0.0, 0.5, 0.0, 0.0))
        self.assertEqual(x, 50.0)
        self.assertEqual(y, 100.0)
        
        # Test with canvas dimensions
        width, height = 1976, 2114
        self.assertTrue(verify_transform_matrix(0, 0, width, height))
        self.assertTrue(verify_transform_matrix(width, height, width, height))
    
    def test_coordinate_range(self):
        """Test coordinate range verification."""
        # Test valid coordinates
        self.assertTrue(verify_coordinate_range(4079.86, 14209.55))  # leftup
        self.assertTrue(verify_coordinate_range(156900.14, 2793.01))  # rightdown
        
        # Test invalid coordinates
        self.assertFalse(verify_coordinate_range(0.0, 0.0))
        self.assertFalse(verify_coordinate_range(200000.0, 20000.0))

if __name__ == '__main__':
    unittest.main()
