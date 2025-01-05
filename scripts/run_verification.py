#!/usr/bin/env python3
import os
import sys
import json
import logging
from datetime import datetime
from verify_all import verify_live_canvas, verify_static_images, verify_coverage
from verify_corners import verify_corner_coordinates, verify_corner_images
from verify_output_size import verify_output_size

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('verification.log')
    ]
)

def run_verification():
    """Run all verification checks and return detailed results."""
    visualization_dir = os.path.join(os.path.dirname(__file__), 'captured_visualization')
    corners_dir = os.path.join(visualization_dir, 'corners')
    
    # Ensure directories exist
    if not os.path.exists(visualization_dir):
        logging.error(f"Directory not found: {visualization_dir}")
        return False
        
    if not os.path.exists(corners_dir):
        logging.error(f"Directory not found: {corners_dir}")
        return False
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    try:
        # Step 1: Verify live canvas properties
        logging.info("\n=== Verifying Canvas Properties ===")
        results['checks']['canvas'] = {
            'status': verify_live_canvas(),
            'requirements': {
                'dimensions': '1976x2114',
                'transform': 'matrix(0.5, 0, 0, 0.5, 0, 0)'
            }
        }
        
        # Step 2: Verify corner coordinates
        logging.info("\n=== Verifying Corner Coordinates ===")
        corner_results = verify_corner_coordinates()
        results['checks']['corners'] = {
            'status': bool(corner_results),
            'coordinates': corner_results,
            'requirements': {
                'leftup': '4079.86,14209.55',
                'rightdown': '156900.14,2793.01',
                'zoom_range': '12.4515-18.0000'
            }
        }
        
        # Step 3: Verify corner images
        logging.info("\n=== Verifying Corner Images ===")
        image_results = verify_corner_images()
        results['checks']['images'] = {
            'status': all(img and img.get('meets_size_requirement') for img in image_results.values() if img),
            'details': image_results
        }
        
        # Step 4: Verify static image properties
        logging.info("\n=== Verifying Static Images ===")
        results['checks']['static'] = {
            'status': verify_static_images(visualization_dir),
            'requirements': {
                'ratio': '1976:2114',
                'size': '10x-100x base size'
            }
        }
        
        # Step 5: Verify coordinate coverage
        logging.info("\n=== Verifying Coverage ===")
        results['checks']['coverage'] = {
            'status': verify_coverage(corners_dir),
            'requirements': {
                'corners': 'leftup to rightdown',
                'zoom_levels': 'all between 12.4515 and 18.0000'
            }
        }
        
        # Step 6: Verify output size
        logging.info("\n=== Verifying Output Size ===")
        results['checks']['size'] = {
            'status': verify_output_size(visualization_dir),
            'requirements': {
                'ratio': '10x-100x base size'
            }
        }
        
        # Calculate overall status
        results['overall_status'] = all(check['status'] for check in results['checks'].values())
        
        # Save results
        with open('verification_results.json', 'w') as f:
            json.dump(results, f, indent=2)
            
        # Print summary
        print("\n=== Verification Summary ===")
        for check_name, check_data in results['checks'].items():
            status = '✓' if check_data['status'] else '✗'
            print(f"{check_name}: {status}")
        print(f"\nOverall Status: {'✓' if results['overall_status'] else '✗'}")
        print("Detailed results saved to verification_results.json")
        
        return results['overall_status']
        
    except Exception as e:
        logging.error(f"Verification failed: {str(e)}")
        return False

if __name__ == '__main__':
    success = run_verification()
    sys.exit(0 if success else 1)
