#!/usr/bin/env python3
import os
import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

def verify_canvas_properties(url=None, timeout=60):
    """Verify canvas dimensions and transform matrix with proper timeout."""
    if url is None:
        url = 'https://calculatingempires.net/'
    print(f"\nVerifying canvas properties for {url}...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=2500,2500')
    options.add_argument('--disable-gpu')
    options.add_argument('--enable-logging')
    options.add_argument('--disable-web-security')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.page_load_strategy = 'eager'
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"\nAttempt {retry_count + 1}/{max_retries}")
                print("Navigating to page...")
                driver.get(url)
                
                # Wait for initial page load with increased timeout
                time.sleep(15)  # Increased initial wait
                
                # Force a page refresh to ensure clean state
                driver.refresh()
                time.sleep(5)
                
                # Wait for canvas presence with increased timeout and better error handling
                try:
                    canvas = WebDriverWait(driver, 45).until(
                        EC.presence_of_element_located((By.TAG_NAME, "canvas"))
                    )
                    print("Canvas element found")
                except TimeoutException:
                    print("Timeout waiting for canvas element")
                    raise
                
                # Break down canvas property checks into separate operations
                print("\nChecking canvas properties step by step...")
                
                # Step 1: Get basic canvas element
                canvas_exists = driver.execute_script("""
                    const canvas = document.querySelector('canvas');
                    return canvas !== null;
                """)
                
                if not canvas_exists:
                    print("❌ Canvas element not found")
                    return False
                
                print("✅ Canvas element found")
                time.sleep(2)  # Wait for canvas to stabilize
                
                # Step 2: Force a resize event and wait
                driver.execute_script("""
                    window.dispatchEvent(new Event('resize'));
                """)
                time.sleep(2)
                
                # Step 3: Get canvas dimensions and verify aspect ratio
                dimensions = driver.execute_script("""
                    const canvas = document.querySelector('canvas');
                    return {
                        width: canvas.width,
                        height: canvas.height,
                        clientWidth: canvas.clientWidth,
                        clientHeight: canvas.clientHeight
                    };
                """)
                
                print("\nCanvas dimensions:")
                print(f"Width: {dimensions['width']} (client: {dimensions['clientWidth']})")
                print(f"Height: {dimensions['height']} (client: {dimensions['clientHeight']})")
                
                # Calculate and verify aspect ratio
                expected_ratio = 1976 / 2114  # approximately 0.935
                actual_ratio = dimensions['width'] / dimensions['height']
                ratio_tolerance = 0.05  # 5% tolerance
                
                ratio_match = abs(actual_ratio - expected_ratio) < ratio_tolerance
                
                if not ratio_match:
                    print("\n❌ Canvas aspect ratio incorrect:")
                    print(f"Expected ratio: {expected_ratio:.3f}")
                    print(f"Actual ratio: {actual_ratio:.3f}")
                    return False
                
                # Verify minimum size requirements
                min_width = 1000  # Ensure canvas is large enough for detailed rendering
                min_height = 1000
                
                if dimensions['width'] < min_width or dimensions['height'] < min_height:
                    print("\n❌ Canvas dimensions too small:")
                    print(f"Minimum required: {min_width}x{min_height}")
                    print(f"Got: {dimensions['width']}x{dimensions['height']}")
                    return False
                
                print("✅ Canvas dimensions and aspect ratio verified")
                
                # Step 4: Get transform matrix
                transform = driver.execute_script("""
                    const canvas = document.querySelector('canvas');
                    const style = window.getComputedStyle(canvas);
                    return style.transform;
                """)
                
                print("\nTransform matrix:")
                print(transform)
                
                # Verify transform matrix
                expected_transform = "matrix(0.5, 0, 0, 0.5, 0, 0)"
                transform_match = (
                    transform.startswith('matrix(') and
                    '0.5' in transform and
                    '0, 0' in transform
                )
                
                if not transform_match:
                    print("\n❌ Transform matrix incorrect:")
                    print(f"Expected: {expected_transform}")
                    print(f"Got: {transform}")
                    return False
                
                print("✅ Transform matrix verified")
                
                # Step 5: Get map properties for debugging
                map_props = driver.execute_script("""
                    const map = window.map;
                    if (!map) return null;
                    return {
                        zoom: map.getView().getZoom(),
                        center: map.getView().getCenter(),
                        resolution: map.getView().getResolution()
                    };
                """)
                
                if map_props:
                    print("\nMap properties:")
                    print(json.dumps(map_props, indent=2))
                
                print("\n✅ All canvas properties verified successfully")
                return True
                
            except Exception as e:
                print(f"\n❌ Attempt {retry_count + 1} failed: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    print("Waiting 10 seconds before retry...")
                    time.sleep(10)
                    continue
                else:
                    print("\n❌ All retry attempts failed")
                    return False
                
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

def verify_all_views():
    """Verify canvas properties at different views and zoom levels."""
    views = {
        'leftup': 'https://calculatingempires.net/?pos=4079.86%2C14209.55%2C14.8544',
        'rightdown': 'https://calculatingempires.net/?pos=156900.14%2C2793.01%2C14.8544'
    }
    
    zoom_levels = []
    current_zoom = 12.4515
    while current_zoom <= 18.0000:
        zoom_levels.append(current_zoom)
        current_zoom = round(current_zoom + 0.66, 4)
    
    results = {
        'views': {},
        'zoom_levels': {}
    }
    
    # Test corner views
    for view_name, url in views.items():
        print(f"\nTesting {view_name} view...")
        results['views'][view_name] = verify_canvas_properties(url)
    
    # Test zoom levels
    base_url = 'https://calculatingempires.net/?pos=93000.24%2C8725.00%2C'
    for zoom in zoom_levels:
        print(f"\nTesting zoom level {zoom}...")
        url = f"{base_url}{zoom}"
        results['zoom_levels'][str(zoom)] = verify_canvas_properties(url)
    
    # Report overall results
    success = all(results['views'].values()) and all(results['zoom_levels'].values())
    
    if success:
        print("\n✅ All canvas properties verified successfully!")
    else:
        print("\n❌ Some verifications failed. Check the logs for details.")
    
    return success

if __name__ == '__main__':
    success = verify_all_views()
    sys.exit(0 if success else 1)
