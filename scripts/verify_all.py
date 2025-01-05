import os
import sys
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time

def verify_live_canvas():
    """Verify canvas properties directly from the webpage with robust initialization checks."""
    print("\nVerifying live canvas properties...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=2500,2500')  # Larger window to ensure full canvas visibility
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')  # Allow cross-origin requests
    options.add_argument('--disable-dev-shm-usage')
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    # Add timeout configuration
    PAGE_LOAD_TIMEOUT = 30
    SCRIPT_TIMEOUT = 30
    IMPLICIT_WAIT = 10
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Navigating to page...")
        driver.get('https://calculatingempires.net/')
        
        print("Waiting for canvas initialization...")
        max_retries = 30
        retry_count = 0
        result = None
        
        while retry_count < max_retries and not result:
            try:
                # Wait for canvas presence
                canvas = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "canvas"))
                )
                
                # Get detailed canvas properties with verification
                result = driver.execute_script("""
                    return new Promise((resolve) => {
                        const checkProperties = () => {
                            const canvas = document.querySelector('canvas');
                            if (!canvas) return null;
                            
                            const style = window.getComputedStyle(canvas);
                            const props = {
                                dimensions: {
                                    width: canvas.width,
                                    height: canvas.height,
                                    clientWidth: canvas.clientWidth,
                                    clientHeight: canvas.clientHeight
                                },
                                transform: {
                                    style: canvas.style.transform,
                                    computed: style.transform,
                                    origin: style.transformOrigin
                                },
                                style: {
                                    position: style.position,
                                    left: style.left,
                                    top: style.top
                                },
                                map: {
                                    initialized: typeof window.map !== 'undefined',
                                    zoom: window.map ? window.map.getView().getZoom() : null,
                                    center: window.map ? window.map.getView().getCenter() : null
                                }
                            };
                            
                            // Check if properties match requirements
                            if (props.dimensions.width === 1976 && 
                                props.dimensions.height === 2114 && 
                                props.transform.computed === 'matrix(0.5, 0, 0, 0.5, 0, 0)' &&
                                props.map.initialized) {
                                resolve(props);
                                return;
                            }
                            
                            console.log('Waiting for correct canvas properties...');
                            console.log('Current:', JSON.stringify(props, null, 2));
                            setTimeout(checkProperties, 1000);
                        };
                        
                        checkProperties();
                    });
                """)
                
                if result:
                    break
                    
            except Exception as e:
                print(f"Retry {retry_count + 1}/{max_retries}: {str(e)}")
            
            retry_count += 1
            time.sleep(1)
            
        if not result: 
            print("\n❌ Failed to verify canvas properties after max retries")
            return False
        
        print("\nLive Canvas Properties:")
        print(json.dumps(result, indent=2))
        
        # Verify dimensions
        dims = result.get('dimensions', {})
        if dims.get('width') != 1976 or dims.get('height') != 2114:
            print("\n❌ Canvas dimensions incorrect:")
            print(f"Expected: 1976x2114")
            print(f"Got: {dims.get('width')}x{dims.get('height')}")
            return False
        
        # Verify transform matrix
        transform = result.get('transform', {})
        expected_transform = "matrix(0.5, 0, 0, 0.5, 0, 0)"
        if transform.get('computed') != expected_transform:
            print("\n❌ Transform matrix incorrect:")
            print(f"Expected: {expected_transform}")
            print(f"Got: {transform.get('computed')}")
            return False
        
        print("\n✅ Live canvas properties verified successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ Live verification failed: {str(e)}")
        return False
    finally:
        driver.quit()

def verify_static_images(output_dir):
    """Verify properties of captured images."""
    print("\nVerifying static image properties...")
    
    # Verify dimensions and transform ratio
    total_pixels = 0
    total_size = 0
    image_count = 0
    base_canvas_pixels = 1976 * 2114
    
    for root, _, files in os.walk(output_dir):
        for f in files:
            if f.endswith('.png'):
                path = os.path.join(root, f)
                with Image.open(path) as img:
                    width, height = img.size
                    total_pixels += width * height
                    total_size += os.path.getsize(path)
                    image_count += 1
                    ratio = width / height
                    if abs(ratio - (1976/2114)) > 0.01:
                        print(f"\n❌ Image ratio incorrect for {f}:")
                        print(f"Expected: {1976/2114:.4f}")
                        print(f"Got: {ratio:.4f}")
                        return False
    
    # Verify total output size (10x-100x larger)
    pixel_ratio = total_pixels / base_canvas_pixels
    print(f"\nOutput pixel ratio: {pixel_ratio:.2f}x")
    print(f"Total pixels: {total_pixels:,}")
    print(f"Base canvas pixels: {base_canvas_pixels:,}")
    
    if pixel_ratio < 10 or pixel_ratio > 100:
        print("❌ Output size ratio not within 10x-100x range")
        print(f"Current ratio: {pixel_ratio:.2f}x")
        print(f"Required range: 10x-100x")
        return False
    
    print("✅ Static image properties verified successfully")
    return True

def verify_coverage(corners_dir):
    """Verify coverage from leftup to rightdown coordinates and zoom levels."""
    print("\nVerifying coordinate coverage and zoom levels...")
    
    corners = {
        'leftup': {'x': 4079.86, 'y': 14209.55, 'z': 14.8544},
        'rightdown': {'x': 156900.14, 'y': 2793.01, 'z': 14.8544}
    }
    
    # Verify corner coverage
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
    
    print("\nCorner Coverage Results:")
    print(json.dumps(results, indent=2))
    
    if not all(r['found'] for r in results.values()):
        print("❌ Missing corner images")
        return False
        
    # Verify zoom levels
    zoom_levels = []
    zoom = 12.4515
    while zoom <= 18.0000:
        zoom_levels.append(zoom)
        zoom += 0.66
        
    zoom_files = []
    for zoom in zoom_levels:
        zoom_str = f"{zoom:.4f}"
        zoom_pattern = f"*_z{zoom_str}.png"
        for root, _, files in os.walk(corners_dir):
            matches = [f for f in files if f.endswith(f"_z{zoom_str}.png")]
            zoom_files.extend([os.path.join(root, f) for f in matches])
    
    print(f"\nFound {len(zoom_files)} zoom level images")
    print(f"Expected zoom levels: {len(zoom_levels)}")
    
    if len(zoom_files) < len(zoom_levels):
        print("❌ Missing zoom level images")
        print(f"Found zoom levels: {sorted(set([float(f.split('_z')[-1].replace('.png', '')) for f in zoom_files]))}")
        return False
    
    print("✅ Coverage and zoom levels verified successfully")
    return True

def main():
    output_dir = 'captured_visualization'
    corners_dir = os.path.join(output_dir, 'corners')
    
    # Run all verifications
    live_ok = verify_live_canvas()
    static_ok = verify_static_images(output_dir)
    coverage_ok = verify_coverage(corners_dir)
    
    # Print final results
    print("\nVerification Results:")
    print(f"Live Canvas Properties: {'✅' if live_ok else '❌'}")
    print(f"Static Image Properties: {'✅' if static_ok else '❌'}")
    print(f"Coordinate Coverage: {'✅' if coverage_ok else '❌'}")
    
    if live_ok and static_ok and coverage_ok:
        print("\n✅ All verifications passed")
        return 0
    else:
        print("\n❌ Some verifications failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
