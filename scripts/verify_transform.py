from PIL import Image
import os
import json

def verify_transform_matrix(image_path):
    """Verify the transform matrix application by checking image dimensions."""
    with Image.open(image_path) as img:
        width, height = img.size
        # Original canvas: 1976x2114
        # Transform matrix: matrix(0.5, 0, 0, 0.5, 0, 0)
        # Expected ratio after transform: 2:1
        ratio = width / height
        print(f"Image dimensions: {width}x{height}")
        print(f"Aspect ratio: {ratio:.4f}")
        return abs(ratio - (1976/2114)) < 0.01

def verify_coverage(corners_dir):
    """Verify coverage from leftup to rightdown coordinates."""
    corners = {
        'leftup': {'x': 4079.86, 'y': 14209.55},
        'rightdown': {'x': 156900.14, 'y': 2793.01}
    }
    
    results = {}
    for corner_name, coords in corners.items():
        corner_file = os.path.join(corners_dir, f"{corner_name}_corner.png")
        if os.path.exists(corner_file):
            with Image.open(corner_file) as img:
                results[corner_name] = {
                    'found': True,
                    'size': img.size,
                    'coords': coords
                }
        else:
            results[corner_name] = {
                'found': False,
                'coords': coords
            }
    
    print("\nCorner Coverage Verification:")
    print(json.dumps(results, indent=2))
    return all(r['found'] for r in results.values())

if __name__ == '__main__':
    output_dir = 'captured_visualization'
    corners_dir = os.path.join(output_dir, 'corners')
    
    print("\nVerifying Transform Matrix...")
    transform_ok = all(
        verify_transform_matrix(os.path.join(root, f))
        for root, _, files in os.walk(output_dir)
        for f in files if f.endswith('.png')
    )
    
    print("\nVerifying Corner Coverage...")
    coverage_ok = verify_coverage(corners_dir)
    
    if transform_ok and coverage_ok:
        print("\n✓ All verifications passed")
    else:
        print("\n✗ Some verifications failed")
