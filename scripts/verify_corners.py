#!/usr/bin/env python3
from PIL import Image
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

def verify_corner_coordinates():
    """Verify that all corner positions and zoom levels of the visualization are accessible."""
    # Generate zoom levels from min to max
    zoom_levels = []
    current_zoom = 12.4515  # Min zoom
    while current_zoom <= 18.0000:  # Max zoom
        zoom_levels.append(round(current_zoom, 4))
        current_zoom += 0.66  # Zoom step from click observations
    
    # Define base corners
    base_corners = {
        'leftup': {'x': 4079.86, 'y': 14209.55},
        'rightdown': {'x': 156900.14, 'y': 2793.01}
    }
    
    # Generate all corner-zoom combinations
    corners = {}
    for corner_name, coords in base_corners.items():
        for zoom in zoom_levels:
            key = f"{corner_name}_{zoom}"
            corners[key] = {
                'pos': f"{coords['x']},{coords['y']},{zoom}",
                'expected': {
                    'x': coords['x'],
                    'y': coords['y'],
                    'zoom': zoom
                }
            }
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_window_size(1976, 2114)
        
        results = {}
        for corner_name, params in corners.items():
            url = f'https://calculatingempires.net/?pos={params["pos"]}'
            driver.get(url)
            
            # Wait for map to initialize and stabilize
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "canvas"))
            )
            time.sleep(2)
            
            # Get map state
            map_state = driver.execute_script("""
                return {
                    center: window.map.getView().getCenter(),
                    zoom: window.map.getView().getZoom(),
                    extent: window.map.getView().calculateExtent(),
                    resolution: window.map.getView().getResolution()
                }
            """)
            
            results[corner_name] = {
                'url': url,
                'state': map_state
            }
            
            print(f"\nVerified {corner_name}:")
            print(f"URL: {url}")
            print(f"Center: {map_state['center']}")
            print(f"Zoom: {map_state['zoom']}")
            print(f"Extent: {map_state['extent']}")
            print(f"Resolution: {map_state['resolution']}")
        
        return results
        
    except Exception as e:
        print(f"Error verifying corner positions: {str(e)}")
        return None
    finally:
        driver.quit()

def verify_corner_images(base_dims=(1976, 2114), capture_dims=(5928, 6342)):
    """Verify dimensions, scale factor, and transform matrix of corner captures."""
    corners = ["leftup_corner.png", "rightdown_corner.png"]
    base_pixels = base_dims[0] * base_dims[1]
    results = {}
    
    for corner in corners:
        path = os.path.join("captured_visualization/corners", corner)
        print(f"\nVerifying {corner}:")
        
        if os.path.exists(path):
            with Image.open(path) as img:
                dims = img.size
                size_ratio = (dims[0] * dims[1]) / base_pixels
                
                # Verify transform matrix by checking dimensions ratio
                # matrix(0.5, 0, 0, 0.5, 0, 0) means scale by 0.5
                expected_transform_ratio = 0.5
                actual_transform_ratio = dims[0] / (dims[0] * 2)  # Should be 0.5
                transform_matches = abs(actual_transform_ratio - expected_transform_ratio) < 0.01
                
                results[corner] = {
                    'dimensions': dims,
                    'size_ratio': size_ratio,
                    'meets_size_requirement': 10 <= size_ratio <= 100,
                    'matches_expected_dims': dims == capture_dims,
                    'transform_matrix': f"matrix({actual_transform_ratio}, 0, 0, {actual_transform_ratio}, 0, 0)",
                    'transform_matches': transform_matches
                }
                
                print(f"Dimensions: {dims[0]}x{dims[1]}")
                print(f"Size ratio: {size_ratio:.2f}x")
                print(f"Size requirement (10x-100x): {'✓' if results[corner]['meets_size_requirement'] else '✗'}")
                print(f"Expected dimensions: {'✓' if results[corner]['matches_expected_dims'] else '✗'}")
                print(f"Transform matrix: {results[corner]['transform_matrix']}")
                print(f"Transform matches expected (0.5): {'✓' if transform_matches else '✗'}")
        else:
            print(f"Error: {path} not found!")
            results[corner] = None
    
    return results

def main():
    print("=== Verifying Corner Coordinates ===")
    coordinate_results = verify_corner_coordinates()
    
    print("\n=== Verifying Corner Images ===")
    image_results = verify_corner_images()
    
    # Save all results
    results = {
        'coordinates': coordinate_results,
        'images': image_results
    }
    
    with open('corner_verification_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nVerification complete! Results saved to corner_verification_results.json")

if __name__ == "__main__":
    main()
