#!/usr/bin/env python3
import os
import json
import math
from PIL import Image

def check_prerequisites():
    """Check if all required files and directories exist."""
    print("\n=== Checking Prerequisites ===")
    required_files = [
        'corner_verification_results.json',
        os.path.join('captured_visualization', 'merged_visualization.png')
    ]
    required_dirs = [
        'downloaded_tiles',
        'captured_visualization'
    ]
    
    missing = []
    for f in required_files:
        if not os.path.isfile(f):
            missing.append(f"File: {f}")
    
    for d in required_dirs:
        if not os.path.isdir(d):
            missing.append(f"Directory: {d}")
    
    if missing:
        print("❌ Missing required files/directories:")
        for m in missing:
            print(f"  - {m}")
        return False
    
    print("✓ All prerequisites found")
    return True

def verify_canvas_dimensions():
    """Verify canvas dimensions and transform matrix from saved data."""
    print("\n=== Verifying Canvas Properties ===")
    try:
        with open('corner_verification_results.json', 'r') as f:
            data = json.load(f)
            canvas_width = data.get('canvas_width', 0)
            canvas_height = data.get('canvas_height', 0)
            transform_matrix = data.get('transform_matrix', '')
            
            if canvas_width != 1976 or canvas_height != 2114:
                print(f"❌ Canvas dimensions mismatch: {canvas_width}x{canvas_height}")
                return False
                
            if transform_matrix != "matrix(0.5, 0, 0, 0.5, 0, 0)":
                print(f"❌ Transform matrix mismatch: {transform_matrix}")
                return False
                
            print("✓ Canvas dimensions verified: 1976x2114")
            print("✓ Transform matrix verified: matrix(0.5, 0, 0, 0.5, 0, 0)")
            return True
    except Exception as e:
        print(f"❌ Failed to verify canvas properties: {str(e)}")
        return False

def verify_coordinate_coverage():
    """Verify coordinate coverage from leftup to rightdown."""
    print("\n=== Verifying Coordinate Coverage ===")
    try:
        leftup = (4079.86, 14209.55)
        rightdown = (156900.14, 2793.01)
        
        with open('corner_verification_results.json', 'r') as f:
            data = json.load(f)
            corners = data.get('corners', {})
            
            if not corners:
                print("❌ No corner data found")
                return False
                
            captured_leftup = corners.get('leftup', {})
            captured_rightdown = corners.get('rightdown', {})
            
            if not captured_leftup or not captured_rightdown:
                print("❌ Missing corner coordinates")
                return False
                
            # Verify coordinates with small tolerance for floating point comparison
            tolerance = 0.01
            if (abs(captured_leftup[0] - leftup[0]) > tolerance or 
                abs(captured_leftup[1] - leftup[1]) > tolerance or
                abs(captured_rightdown[0] - rightdown[0]) > tolerance or
                abs(captured_rightdown[1] - rightdown[1]) > tolerance):
                print("❌ Coordinate coverage mismatch")
                return False
                
            print("✓ Coordinate coverage verified")
            return True
    except Exception as e:
        print(f"❌ Failed to verify coordinate coverage: {str(e)}")
        return False

def verify_zoom_range():
    """Verify zoom range from 12.4515 to 18.0000."""
    print("\n=== Verifying Zoom Range ===")
    try:
        with open('corner_verification_results.json', 'r') as f:
            data = json.load(f)
            min_zoom = float(data.get('min_zoom', 0))
            max_zoom = float(data.get('max_zoom', 0))
            
            if min_zoom > 12.4515 or max_zoom < 18.0000:
                print(f"❌ Zoom range mismatch: {min_zoom} to {max_zoom}")
                return False
                
            print(f"✓ Zoom range verified: {min_zoom} to {max_zoom}")
            return True
    except Exception as e:
        print(f"❌ Failed to verify zoom range: {str(e)}")
        return False

def verify_output_size():
    """Verify output is 10x-100x larger than current implementation."""
    print("\n=== Verifying Output Size ===")
    try:
        # Get base canvas size
        base_size = 1976 * 2114
        
        # Get merged visualization size
        merged_path = os.path.join('captured_visualization', 'merged_visualization.png')
        if not os.path.exists(merged_path):
            print("❌ Merged visualization not found")
            return False
            
        with Image.open(merged_path) as img:
            output_size = img.width * img.height
            size_ratio = output_size / base_size
            
            if size_ratio < 10 or size_ratio > 100:
                print(f"❌ Output size ratio not in range: {size_ratio:.2f}x")
                return False
                
            print(f"✓ Output size verified: {size_ratio:.2f}x larger")
            return True
    except Exception as e:
        print(f"❌ Failed to verify output size: {str(e)}")
        return False

def verify_data_completeness():
    """Verify complete data capture."""
    print("\n=== Verifying Data Completeness ===")
    try:
        # Check tile coverage
        tile_dir = 'downloaded_tiles'
        if not os.path.exists(tile_dir):
            print("❌ No downloaded tiles found")
            return False
            
        # Count tiles and verify against expected count
        total_tiles = sum(len(files) for _, _, files in os.walk(tile_dir))
        min_expected_tiles = 1000  # Adjust based on zoom levels and coverage
        
        if total_tiles < min_expected_tiles:
            print(f"❌ Insufficient tile count: {total_tiles} < {min_expected_tiles}")
            return False
            
        print(f"✓ Data completeness verified: {total_tiles} tiles")
        return True
    except Exception as e:
        print(f"❌ Failed to verify data completeness: {str(e)}")
        return False

def main():
    """Run all verifications."""
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Cannot proceed with verification.")
        return 1
        
    results = {
        "canvas_properties": verify_canvas_dimensions(),
        "coordinate_coverage": verify_coordinate_coverage(),
        "zoom_range": verify_zoom_range(),
        "output_size": verify_output_size(),
        "data_completeness": verify_data_completeness()
    }
    
    print("\n=== Verification Summary ===")
    all_passed = all(results.values())
    for check, passed in results.items():
        status = "✓" if passed else "❌"
        print(f"{status} {check}")
    
    if all_passed:
        print("\n✅ All verifications passed!")
    else:
        print("\n❌ Some verifications failed!")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
