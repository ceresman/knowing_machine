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

def verify_canvas_at_position(driver, x, y, zoom):
    """Verify canvas properties at a specific position and zoom level."""
    url = f"https://calculatingempires.net/?pos={x},{y},{zoom}"
    print(f"\nVerifying canvas at {url}")
    driver.get(url)
    
    # Wait for map initialization
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return typeof window.map !== 'undefined' && window.map.getView() !== null")
    )
    
    # Get canvas element and wait for it to stabilize
    canvas = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "canvas"))
    )
    time.sleep(5)
    
    # Force map update
    driver.execute_script("""
        window.map.updateSize();
        window.map.render();
        return new Promise(resolve => setTimeout(resolve, 2000));
    """)
    
    # Get canvas properties
    props = driver.execute_script("""
        const canvas = document.querySelector('canvas');
        const computed = window.getComputedStyle(canvas);
        return {
            dimensions: {
                width: canvas.width,
                height: canvas.height
            },
            transform: computed.transform,
            transformOrigin: computed.transformOrigin
        };
    """)
    
    return props

def verify_tile_completeness():
    """Verify that all required tiles are downloaded and not corrupted."""
    print("\nVerifying tile completeness...")
    
    tiles_dir = 'downloaded_tiles'
    if not os.path.exists(tiles_dir):
        print("\n❌ Tiles directory not found")
        return False
    
    try:
        # Get all zoom levels
        zoom_levels = sorted([d for d in os.listdir(tiles_dir) if os.path.isdir(os.path.join(tiles_dir, d))])
        if not zoom_levels:
            print("\n❌ No zoom levels found")
            return False
        
        total_tiles = 0
        corrupted_tiles = 0
        missing_tiles = 0
        
        # Expected zoom levels
        expected_zooms = []
        current_zoom = 12.4515
        while current_zoom <= 18.0000:
            expected_zooms.append(str(int(current_zoom)))
            current_zoom += 0.66
        
        # Check for missing zoom levels
        missing_zooms = set(expected_zooms) - set(zoom_levels)
        if missing_zooms:
            print(f"\n❌ Missing zoom levels: {sorted(missing_zooms)}")
            return False
        
        for zoom in zoom_levels:
            zoom_dir = os.path.join(tiles_dir, zoom)
            x_dirs = [d for d in os.listdir(zoom_dir) if os.path.isdir(os.path.join(zoom_dir, d))]
            
            for x_dir in x_dirs:
                x_path = os.path.join(zoom_dir, x_dir)
                y_files = [f for f in os.listdir(x_path) if f.endswith('.png')]
                
                # Calculate expected tile range for this zoom level
                z = int(zoom)
                expected_x_range = range(0, 2**z)
                expected_y_range = range(0, 2**z)
                
                # Check for missing tiles
                for x in expected_x_range:
                    for y in expected_y_range:
                        tile_name = f"{y}.png"
                        tile_path = os.path.join(x_path, tile_name)
                        
                        if not os.path.exists(tile_path):
                            print(f"\n❌ Missing tile: zoom={zoom}, x={x}, y={y}")
                            missing_tiles += 1
                            continue
                        
                        total_tiles += 1
                        
                        # Verify tile integrity
                        try:
                            with Image.open(tile_path) as img:
                                img.verify()
                        except Exception as e:
                            print(f"\n❌ Corrupted tile: {tile_path}")
                            print(f"Error: {str(e)}")
                            corrupted_tiles += 1
        
        if missing_tiles > 0:
            print(f"\n❌ Found {missing_tiles} missing tiles")
            return False
            
        if corrupted_tiles > 0:
            print(f"\n❌ Found {corrupted_tiles} corrupted tiles out of {total_tiles}")
            return False
        
        print(f"\n✅ All {total_tiles} tiles verified successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to verify tiles: {str(e)}")
        return False

def verify_live_canvas():
    """Verify canvas properties directly from the webpage with robust initialization checks."""
    print("\nVerifying live canvas properties...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1976,2114')  # Match expected canvas size
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    try:
        service = Service(ChromeDriverManager().install())
        with webdriver.Chrome(service=service, options=options) as driver:
            # Test corner positions
            corners = {
                'leftup': {'x': 4079.86, 'y': 14209.55, 'z': 14.8544},
                'rightdown': {'x': 156900.14, 'y': 2793.01, 'z': 14.8544}
            }
            
            # Test zoom levels
            zoom_levels = []
            current_zoom = 12.4515
            while current_zoom <= 18.0000:
                zoom_levels.append(current_zoom)
                current_zoom += 0.66
            
            # Verify corners
            for corner, pos in corners.items():
                print(f"\nTesting {corner} corner...")
                props = verify_canvas_at_position(driver, pos['x'], pos['y'], pos['z'])
                
                # Verify dimensions with 5% tolerance
                dims = props['dimensions']
                width_tolerance = abs(dims['width'] - 1976) / 1976
                height_tolerance = abs(dims['height'] - 2114) / 2114
                
                if width_tolerance > 0.05 or height_tolerance > 0.05:
                    print(f"\n❌ Canvas dimensions outside tolerance for {corner}:")
                    print(f"Expected: 1976x2114")
                    print(f"Got: {dims['width']}x{dims['height']}")
                    return False
                
                # Verify transform matrix
                if not props['transform'].startswith('matrix(0.5, 0, 0, 0.5'):
                    print(f"\n❌ Transform matrix incorrect for {corner}:")
                    print(f"Expected to start with: matrix(0.5, 0, 0, 0.5")
                    print(f"Got: {props['transform']}")
                    return False
            
            # Verify zoom levels
            print("\nTesting zoom levels...")
            for zoom in zoom_levels:
                print(f"\nTesting zoom level {zoom}...")
                props = verify_canvas_at_position(driver, 93000.24, 8725.00, zoom)
                
                # Verify dimensions with 5% tolerance
                dims = props['dimensions']
                width_tolerance = abs(dims['width'] - 1976) / 1976
                height_tolerance = abs(dims['height'] - 2114) / 2114
                
                if width_tolerance > 0.05 or height_tolerance > 0.05:
                    print(f"\n❌ Canvas dimensions outside tolerance for zoom {zoom}:")
                    print(f"Expected: 1976x2114")
                    print(f"Got: {dims['width']}x{dims['height']}")
                    return False
                
                # Verify transform matrix
                if not props['transform'].startswith('matrix(0.5, 0, 0, 0.5'):
                    print(f"\n❌ Transform matrix incorrect for zoom {zoom}:")
                    print(f"Expected to start with: matrix(0.5, 0, 0, 0.5")
                    print(f"Got: {props['transform']}")
                    return False
            
            print("\n✅ All zoom levels verified successfully")
            print("\n✅ All canvas properties verified successfully")
            return True
            
    except Exception as e:
        print(f"\n❌ Live verification failed: {str(e)}")
        return False
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Test corner positions
        corners = {
            'leftup': {'x': 4079.86, 'y': 14209.55, 'z': 14.8544},
            'rightdown': {'x': 156900.14, 'y': 2793.01, 'z': 14.8544}
        }
        
        # Test zoom levels
        zoom_levels = []
        current_zoom = 12.4515
        while current_zoom <= 18.0000:
            zoom_levels.append(current_zoom)
            current_zoom += 0.66
        
        # Verify corners
        corner_results = {}
        for corner, pos in corners.items():
            print(f"\nTesting {corner} corner...")
            props = verify_canvas_at_position(driver, pos['x'], pos['y'], pos['z'])
            corner_results[corner] = props
            
            # Verify dimensions with 5% tolerance
            dims = props['dimensions']
            width_tolerance = abs(dims['width'] - 1976) / 1976
            height_tolerance = abs(dims['height'] - 2114) / 2114
            
            if width_tolerance > 0.05 or height_tolerance > 0.05:
                print(f"\n❌ Canvas dimensions outside tolerance for {corner}:")
                print(f"Expected: 1976x2114")
                print(f"Got: {dims['width']}x{dims['height']}")
                return False
            
            # Verify transform matrix
            if not props['transform'].startswith('matrix(0.5, 0, 0, 0.5'):
                print(f"\n❌ Transform matrix incorrect for {corner}:")
                print(f"Expected to start with: matrix(0.5, 0, 0, 0.5")
                print(f"Got: {props['transform']}")
                return False
        
        # Verify zoom levels
        print("\nTesting zoom levels...")
        for zoom in zoom_levels:
            print(f"\nTesting zoom level {zoom}...")
            props = verify_canvas_at_position(driver, 93000.24, 8725.00, zoom)
            print(f"Zoom {zoom} properties:", json.dumps(props, indent=2))
                
            # Verify zoom levels
            print("\nTesting zoom levels...")
            zoom_results = {}
            for zoom in zoom_levels:
                print(f"\nTesting zoom level {zoom}...")
                props = verify_canvas_at_position(driver, 93000.24, 8725.00, zoom)
                zoom_results[zoom] = props
                
                # Verify dimensions with 5% tolerance
                dims = props['dimensions']
                width_tolerance = abs(dims['width'] - 1976) / 1976
                height_tolerance = abs(dims['height'] - 2114) / 2114
                
                if width_tolerance > 0.05 or height_tolerance > 0.05:
                    print(f"\n❌ Canvas dimensions outside tolerance for zoom {zoom}:")
                    print(f"Expected: 1976x2114")
                    print(f"Got: {dims['width']}x{dims['height']}")
                    return False
                
                # Verify transform matrix
                if not props['transform'].startswith('matrix(0.5, 0, 0, 0.5'):
                    print(f"\n❌ Transform matrix incorrect for zoom {zoom}:")
                    print(f"Expected to start with: matrix(0.5, 0, 0, 0.5")
                    print(f"Got: {props['transform']}")
                    return False
            
            print("\n✅ All zoom levels verified successfully")
            print("\n✅ All canvas properties verified successfully")
            return True
                
                # Get basic canvas properties
                result = driver.execute_script("""
                    const canvas = document.querySelector('canvas');
                    const style = window.getComputedStyle(canvas);
                    return {
                        dimensions: {
                            width: canvas.width,
                            height: canvas.height
                        },
                        transform: style.transform
                    };
                """)
                
                if not result:
                    print("Failed to get canvas properties")
                    return False
                    
                print("\nCanvas Properties:")
                print(json.dumps(result, indent=2))
                
        except Exception as e:
            print(f"\n❌ Canvas verification failed: {str(e)}")
            return False
            
        finally:
            driver.quit()
        
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
    tiles_ok = verify_tile_completeness()
    static_ok = verify_static_images(output_dir)
    coverage_ok = verify_coverage(corners_dir)
    
    # Print final results
    print("\nVerification Results:")
    print(f"Live Canvas Properties: {'✅' if live_ok else '❌'}")
    print(f"Tile Completeness: {'✅' if tiles_ok else '❌'}")
    print(f"Static Image Properties: {'✅' if static_ok else '❌'}")
    print(f"Coordinate Coverage: {'✅' if coverage_ok else '❌'}")
    
    if live_ok and tiles_ok and static_ok and coverage_ok:
        print("\n✅ All verifications passed")
        return 0
    else:
        print("\n❌ Some verifications failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
