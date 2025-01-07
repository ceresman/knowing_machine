from PIL import Image
import os
import sys
from typing import Dict, Tuple

def verify_dimensions(image_path: str) -> bool:
    """Verify image dimensions and scale factor."""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            print(f"Image dimensions: {width}x{height}")
            
            # Base dimensions from canvas
            base_width, base_height = 1976, 2114
            
            # Calculate scale factor
            scale_factor = width / base_width
            print(f"Scale factor: {scale_factor:.2f}x")
            print(f"Expected scale factor: 3.00x")
            
            # Verify aspect ratio is maintained
            aspect_ratio_original = base_width / base_height
            aspect_ratio_current = width / height
            ratio_diff = abs(aspect_ratio_original - aspect_ratio_current)
            
            if ratio_diff > 0.01:  # Allow 1% difference
                print("✗ Aspect ratio mismatch")
                print(f"  Original: {aspect_ratio_original:.4f}")
                print(f"  Current:  {aspect_ratio_current:.4f}")
                print(f"  Diff:     {ratio_diff:.4f}")
                return False
            else:
                print("✓ Aspect ratio maintained")
            
            # Verify scale matches expected 3x
            scale_diff = abs(scale_factor - 3.0)
            if scale_diff > 0.1:  # Allow 0.1 difference
                print("✗ Scale factor does not match expected 3x")
                return False
            else:
                print("✓ Scale factor matches expected 3x")
            
            # Verify size requirement
            if 10 <= scale_factor <= 100:
                print("✓ Size ratio meets 10x-100x requirement")
                return True
            else:
                print("✗ Size ratio does not meet 10x-100x requirement")
                print(f"  Required: 10x-100x")
                print(f"  Current:  {scale_factor:.2f}x")
                return False
                
    except FileNotFoundError:
        print(f"Error: File not found - {image_path}")
        return False
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return False

def verify_coverage(base_dir: str) -> bool:
    """Verify corner positions are captured."""
    corners = {
        "leftup": (4079.86, 14209.55),
        "rightdown": (156900.14, 2793.01)
    }
    
    missing = []
    for corner, coords in corners.items():
        path = os.path.join(base_dir, "corners", f"{corner}_corner.png")
        if not os.path.exists(path):
            missing.append(f"{corner} at {coords}")
    
    if missing:
        print("✗ Missing corner captures:")
        for m in missing:
            print(f"  - {m}")
        return False
    
    print("✓ All corner positions captured")
    return True

def verify_zoom_levels(base_dir: str) -> bool:
    """Verify all required zoom levels are captured."""
    required_levels = [
        12.4515,  # Base zoom
        13.1115,  # First increment
        13.7715,  # Second increment
        14.8544,  # Corner capture zoom
        16.0000,  # Mid-range zoom
        18.0000   # Maximum detail
    ]
    
    missing = []
    for zoom in required_levels:
        zoom_dir = os.path.join(base_dir, f'zoom_{zoom:.4f}')
        if not os.path.exists(zoom_dir):
            missing.append(f"{zoom:.4f}")
    
    if missing:
        print("✗ Missing zoom levels:")
        for m in missing:
            print(f"  - {m}")
        return False
    
    print("✓ All required zoom levels captured")
    return True

def verify_transform_matrix(image_path: str) -> bool:
    """Verify transform matrix application."""
    try:
        with Image.open(image_path) as img:
            # Check if image has metadata about transform
            if hasattr(img, "info") and "transform_matrix" in img.info:
                matrix = img.info["transform_matrix"]
                expected = "matrix(0.5, 0, 0, 0.5, 0, 0)"
                if matrix == expected:
                    print("✓ Transform matrix correctly applied")
                    return True
            
            # If no metadata, verify scale factor
            width, height = img.size
            base_width, base_height = 1976, 2114
            scale_x = width / base_width
            scale_y = height / base_height
            
            # Allow 1% difference in scale factors
            if abs(scale_x - scale_y) <= 0.01:
                print("✓ Uniform scaling verified (transform matrix equivalent)")
                return True
            else:
                print("✗ Non-uniform scaling detected")
                return False
                
    except Exception as e:
        print(f"Error checking transform: {str(e)}")
        return False

def main():
    """Main verification function."""
    base_dir = "captured_visualization"
    merged_path = "merged_visualization.png"
    
    if not os.path.exists(merged_path):
        print(f"Error: {merged_path} not found")
        sys.exit(1)
    
    print("\nVerifying merged visualization...")
    print("=" * 40)
    
    # Track verification results
    results = []
    
    # Verify dimensions and scale
    results.append(verify_dimensions(merged_path))
    
    # Verify corner coverage
    results.append(verify_coverage(base_dir))
    
    # Verify zoom levels
    results.append(verify_zoom_levels(base_dir))
    
    # Verify transform matrix
    results.append(verify_transform_matrix(merged_path))
    
    # Overall verification result
    print("\nOverall verification result:")
    print("=" * 40)
    if all(results):
        print("✓ All verification checks passed")
        sys.exit(0)
    else:
        print("✗ Some verification checks failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
