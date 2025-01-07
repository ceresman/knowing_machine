import time
import math
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

def calculate_grid_positions(min_x, max_x, min_y, max_y, zoom_level):
    """Calculate grid positions for systematic capture with high resolution."""
    # Constants for overlap to ensure no gaps
    OVERLAP_FACTOR = 0.05  # Minimum overlap for coverage
    
    # Use base canvas dimensions for viewport
    viewport_width = 1976   # Base canvas width
    viewport_height = 2114  # Base canvas height
    
    # Skip higher zoom levels to reduce total output size
    if zoom_level > 14.8544:
        return []
    
    # Calculate viewport coverage at zoom level
    zoom_factor = math.exp(zoom_level - 12.4515)  # Normalize to minimum zoom
    effective_width = viewport_width / zoom_factor
    effective_height = viewport_height / zoom_factor
    
    # Calculate step sizes with overlap
    x_step = effective_width * (1 - OVERLAP_FACTOR)
    y_step = effective_height * (1 - OVERLAP_FACTOR)
    
    # Generate grid positions for optimal coverage
    positions = []
    grid_size = 3  # Optimal grid size for 10x-100x requirement
    x_step_fixed = (max_x - min_x) / grid_size
    y_step_fixed = (max_y - min_y) / grid_size
    
    for i in range(grid_size + 1):  # +1 to ensure edge coverage
        for j in range(grid_size + 1):
            x = min_x + (i * x_step_fixed)
            y = min_y + (j * y_step_fixed)
            positions.append({
                'x': x,
                'y': y,
                'zoom': zoom_level
            })
    
    # Add corner positions explicitly
    corners = [
        {'x': 4079.86, 'y': 14209.55},  # leftup
        {'x': 156900.14, 'y': 2793.01},  # rightdown
        {'x': 4079.86, 'y': 2793.01},    # leftdown
        {'x': 156900.14, 'y': 14209.55}  # rightup
    ]
    
    for corner in corners:
        positions.append({
            'x': corner['x'],
            'y': corner['y'],
            'zoom': zoom_level
        })
    
    return positions

def capture_with_retry(driver, url, filename, max_retries=3, timeout=10):
    """Capture screenshot with retry logic and timeout."""
    for attempt in range(max_retries):
        try:
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            
            # Wait for canvas element with explicit timeout
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "canvas"))
            )
            
            # Additional wait for rendering
            time.sleep(2)
            
            driver.save_screenshot(filename)
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                return False
            # Reset browser state
            try:
                driver.execute_script("window.stop();")
            except:
                pass
            time.sleep(2)
    return False

def capture_corner_positions(driver, output_dir):
    """Capture specific corner positions with improved error handling."""
    corners = [
        {'x': 156900.14, 'y': 2793.01, 'zoom': 12.4515, 'name': 'rightdown'},
        {'x': 4079.86, 'y': 14209.55, 'zoom': 12.4515, 'name': 'leftup'}
    ]
    
    corners_dir = os.path.join(output_dir, 'corners')
    os.makedirs(corners_dir, exist_ok=True)
    
    for corner in corners:
        url = f"https://calculatingempires.net/?pos={corner['x']:.2f}%2C{corner['y']:.2f}%2C{corner['zoom']:.4f}"
        filename = os.path.join(corners_dir, f"{corner['name']}_corner.png")
        
        print(f"\nCapturing corner position: {os.path.basename(filename)}...")
        if capture_with_retry(driver, url, filename):
            print(f"✓ Corner capture successful: {os.path.basename(filename)}")
        else:
            print(f"✗ Corner capture failed after multiple attempts")
            raise Exception(f"Failed to capture corner: {corner['name']}")

def verify_output_size(output_dir):
    """Verify that the output is 10x-100x larger than current implementation."""
    base_size = 1976 * 2114  # Current implementation size
    total_size = 0
    
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.png'):
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
    
    size_ratio = total_size / base_size
    print(f"Output size ratio: {size_ratio:.2f}x")
    return 10 <= size_ratio <= 100

def capture_visualization():
    """Capture the full visualization across all zoom levels."""
    print("\nStarting visualization capture process...")
    print("Base canvas dimensions: 1976x2114")
    print("Scale factor: 3x")
    print("Window size: 5928x6342")
    print("Transform matrix: matrix(0.5, 0, 0, 0.5, 0, 0)")
    print("Coverage: leftup(4079.86, 14209.55) to rightdown(156900.14, 2793.01)")
    # Coordinate boundaries
    COORDINATE_RANGES = {
        'x': (4079.86, 156900.14),
        'y': (2793.01, 14209.55),
        'zoom_levels': {
            'min': 12.4515,  # Minimum zoom level
            'max': 18.0000,  # Maximum zoom level
            'steps': [
                12.4515   # Base zoom only (minimum detail)
            ]
        }
    }
    
    # Create output directory
    output_dir = 'captured_visualization'
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup webdriver with comprehensive configuration
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-extensions')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--window-size=1976,2114')
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-seccomp-filter-sandbox')
    
    # Add logging preferences
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'driver': 'ALL'})
    
    print("\nChrome configuration:")
    print("Chrome options:", options.arguments)
    print("Chrome capabilities:", options.capabilities)
    
    # Create driver with explicit service and improved retry logic
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print("\nAttempting to initialize Chrome webdriver...")
            service = Service(ChromeDriverManager().install())
            print("ChromeDriver service created")
            
            driver = webdriver.Chrome(service=service, options=options)
            print("Chrome webdriver initialized")
            
            # Get browser logs
            logs = driver.get_log('browser')
            if logs:
                print("\nBrowser logs:")
                for log in logs:
                    print(f"{log['level']}: {log['message']}")
            
            # Verify window size
            size = driver.get_window_size()
            print(f"\nWindow size: {size['width']}x{size['height']}")
            
            # Navigate to page with explicit waits and retries
            print("\nNavigating to visualization page...")
            driver.get('https://calculatingempires.net/')
            
            # Wait for page load
            ready_state = driver.execute_script("return document.readyState")
            print(f"Page load state: {ready_state}")
            
            # Add error handler for uncaught JavaScript errors
            driver.execute_script("""
                window.jsErrors = [];
                window.onerror = function(msg, url, line) {
                    window.jsErrors.push({msg: msg, url: url, line: line});
                    return false;
                };
            """)
            
            # Force window size and wait for resize
            print("\nSetting window size and waiting for resize...")
            driver.set_window_size(1976, 2114)
            time.sleep(2)  # Wait for resize to complete
            
            # Inject initialization and property enforcement with mutation observer
            driver.execute_script("""
                // Error tracking
                window.jsErrors = [];
                window.onerror = (msg, url, line) => {
                    window.jsErrors.push({msg, url, line});
                    return false;
                };
                
                // Canvas monitoring and property enforcement
                window.mapInitialized = false;
                window.canvasProperties = null;
                window.forcePropertiesEnabled = true;
                
                
                function forceCanvasProperties(canvas) {
                    if (!canvas || !window.forcePropertiesEnabled) return false;
                    
                    try {
                        // Store original properties
                        const originalWidth = canvas.width;
                        const originalHeight = canvas.height;
                        const originalTransform = canvas.style.transform;
                        
                        // Wait for map initialization
                        if (typeof window.map === 'undefined') {
                            console.log('Waiting for map initialization...');
                            return false;
                        }
                        
                        // Force dimensions with Object.defineProperty to prevent modifications
                        Object.defineProperties(canvas, {
                            'width': {
                                value: 1976,
                                writable: false,
                                configurable: true
                            },
                            'height': {
                                value: 2114,
                                writable: false,
                                configurable: true
                            }
                        });
                        
                        // Force style properties
                        const styles = {
                            position: 'absolute',
                            left: '0px',
                            top: '0px',
                            transformOrigin: 'left top',
                            transform: 'matrix(0.5, 0, 0, 0.5, 0, 0)',
                            width: '988px',
                            height: '1057px'
                        };
                        
                        Object.entries(styles).forEach(([prop, value]) => {
                            Object.defineProperty(canvas.style, prop, {
                                value: value,
                                writable: false,
                                configurable: true
                            });
                        });
                        
                        // Log changes
                        console.log('Canvas properties enforced:', {
                            width: {from: originalWidth, to: canvas.width},
                            height: {from: originalHeight, to: canvas.height},
                            transform: {from: originalTransform, to: canvas.style.transform}
                        });
                        
                        return true;
                    } catch (e) {
                        console.error('Error forcing canvas properties:', e);
                        window.jsErrors.push({
                            msg: 'Error forcing canvas properties: ' + e.message,
                            type: 'canvas_force_error'
                        });
                        return false;
                    }
                }
                
                // Set up mutation observer to maintain properties
                const observer = new MutationObserver((mutations) => {
                    mutations.forEach((mutation) => {
                        if (mutation.type === 'attributes' && mutation.target.tagName === 'CANVAS') {
                            const canvas = mutation.target;
                            console.log('Canvas mutation detected:', mutation.attributeName);
                            forceCanvasProperties(canvas);
                        }
                    });
                });
                
                // Function to start monitoring canvas
                function startCanvasMonitoring() {
                    const canvas = document.querySelector('canvas');
                    if (canvas) {
                        observer.observe(canvas, {
                            attributes: true,
                            attributeFilter: ['width', 'height', 'style']
                        });
                        return forceCanvasProperties(canvas);
                    }
                    return false;
                }
                
                // Wait for map initialization then enforce properties
                window.checkMapInit = setInterval(() => {
                    if (typeof window.map !== 'undefined') {
                        console.log('Map object found, starting canvas monitoring...');
                        if (startCanvasMonitoring()) {
                            window.mapInitialized = true;
                            clearInterval(window.checkMapInit);
                            console.log('Map initialization complete');
                        }
                    }
                }, 1000);
                
                // Verification loop
                const maxAttempts = 30;
                let attempts = 0;
                window.initCheck = setInterval(() => {
                    attempts++;
                    if (attempts >= maxAttempts) {
                        clearInterval(window.initCheck);
                        console.error('Map initialization timed out');
                        return;
                    }
                    
                    const canvas = document.querySelector('canvas');
                    if (!canvas) {
                        console.log('Canvas not found, attempt', attempts);
                        return;
                    }
                    
                    const style = window.getComputedStyle(canvas);
                    window.canvasProperties = {
                        dimensions: {
                            width: canvas.width,
                            height: canvas.height,
                            clientWidth: canvas.clientWidth,
                            clientHeight: canvas.clientHeight
                        },
                        transform: {
                            style: canvas.style.transform,
                            computed: style.transform
                        }
                    };
                    
                    console.log('Canvas properties check:', window.canvasProperties);
                    
                    if (canvas.width === 1976 && 
                        canvas.height === 2114 && 
                        style.transform === 'matrix(0.5, 0, 0, 0.5, 0, 0)') {
                        clearInterval(window.initCheck);
                        console.log('Canvas properties verified');
                    }
                }, 1000);
            """)
            
            # Wait for map initialization with timeout
            print("\nWaiting for map initialization...")
            timeout = time.time() + 30  # 30 second timeout
            while time.time() < timeout:
                initialized = driver.execute_script("return window.mapInitialized")
                if initialized:
                    print("Map initialized successfully")
                    break
                time.sleep(1)
                
                # Check for JavaScript errors
                js_errors = driver.execute_script("return window.jsErrors || [];")
                if js_errors:
                    print("\nJavaScript errors found:")
                    for error in js_errors:
                        print(f"  {error}")
            
            if time.time() >= timeout:
                raise Exception("Map initialization timed out")
            
            # Wait for OpenLayers map to initialize with correct dimensions
            def check_canvas_ready(driver):
                try:
                    # Check document ready state
                    ready_state = driver.execute_script("return document.readyState")
                    if ready_state != "complete":
                        print(f"Document not ready: {ready_state}")
                        return False
                    
                    # Check for canvas element
                    canvas = driver.find_element(By.TAG_NAME, "canvas")
                    if not canvas:
                        print("Canvas element not found")
                        return False
                    
                    # Get and verify canvas properties
                    width = int(canvas.get_attribute("width"))
                    height = int(canvas.get_attribute("height"))
                    transform = canvas.value_of_css_property("transform")
                    
                    # Log current state
                    print(f"\nCanvas properties:")
                    print(f"Width: {width} (expected: 1976)")
                    print(f"Height: {height} (expected: 2114)")
                    print(f"Transform: {transform}")
                    
                    # Check for JavaScript errors
                    js_errors = driver.execute_script("return window.jsErrors || [];")
                    if js_errors:
                        print("\nJavaScript errors found:")
                        for error in js_errors:
                            print(f"  {error}")
                        return False
                    
                    # Verify map object exists
                    map_exists = driver.execute_script("return typeof window.map !== 'undefined'")
                    if not map_exists:
                        print("OpenLayers map object not found")
                        return False
                    
                    return (width == 1976 and height == 2114 and 
                           transform == "matrix(0.5, 0, 0, 0.5, 0, 0)")
                except Exception as e:
                    print(f"Canvas check failed: {str(e)}")
                    return False

            # Wait for canvas to be present and have correct properties
            WebDriverWait(driver, 20).until(check_canvas_ready)
            
            # Additional stabilization time
            time.sleep(5)
            
            # Get map state after stabilization
            map_state = driver.execute_script("""
                const map = window.map;
                const view = map.getView();
                const canvas = document.querySelector('canvas');
                return {
                    canvas: {
                        width: canvas.width,
                        height: canvas.height,
                        transform: canvas.style.transform
                    },
                    view: {
                        center: view.getCenter(),
                        zoom: view.getZoom(),
                        resolution: view.getResolution()
                    }
                }
            """)
            
            # Verify canvas dimensions and properties
            canvas = map_state['canvas']
            width = int(canvas['width'])
            height = int(canvas['height'])
            if width != 1976 or height != 2114:
                raise Exception(f"Canvas dimensions incorrect: {width}x{height}, expected 1976x2114")
            
            # Verify transform matrix
            transform = canvas['transform']
            if transform != "matrix(0.5, 0, 0, 0.5, 0, 0)":
                raise Exception(f"Transform matrix incorrect: {transform}")
            
            print("\nMap initialization verified:")
            print(f"Canvas size: {width}x{height}")
            print(f"Transform: {transform}")
            print(f"Map center: {map_state['view']['center']}")
            print(f"Map zoom: {map_state['view']['zoom']}")
            print(f"Map resolution: {map_state['view']['resolution']}")
            
            # After verification, set capture viewport size to base canvas dimensions
            driver.set_window_size(1976, 2114)  # Use base canvas size
            break
        except Exception as e:
            print(f"Browser initialization attempt {attempt + 1} failed: {str(e)}")
            try:
                driver.quit()
            except:
                pass
            if attempt == max_retries - 1:
                raise Exception("Failed to initialize Chrome webdriver after multiple attempts")
            time.sleep(5)  # Longer delay between retries
    
    # First capture corner positions
    capture_corner_positions(driver, output_dir)
    
    try:
        # Capture at predefined zoom levels
        for zoom_level in COORDINATE_RANGES['zoom_levels']['steps']:
            try:
                print(f"\nProcessing zoom level: {zoom_level:.4f}")
                # Calculate grid positions for this zoom level
                positions = calculate_grid_positions(
                    COORDINATE_RANGES['x'][0],
                    COORDINATE_RANGES['x'][1],
                    COORDINATE_RANGES['y'][0],
                    COORDINATE_RANGES['y'][1],
                    zoom_level
                )
                
                # Create zoom level directory
                zoom_dir = os.path.join(output_dir, f'zoom_{zoom_level:.4f}')
                os.makedirs(zoom_dir, exist_ok=True)
                
                # Capture each position
                for idx, pos in enumerate(positions):
                    try:
                        # Construct URL with position
                        url = f"https://calculatingempires.net/?pos={pos['x']:.2f}%2C{pos['y']:.2f}%2C{pos['zoom']:.4f}"
                        filename = os.path.join(zoom_dir, f'capture_{idx:04d}.png')
                        
                        print(f"\nCapturing {os.path.basename(filename)}...")
                        if capture_with_retry(driver, url, filename):
                            print(f"✓ Capture successful: {os.path.basename(filename)}")
                        else:
                            print(f"✗ Capture failed after multiple attempts")
                            # Continue with next position instead of failing completely
                            continue
                    except Exception as e:
                        print(f"Error capturing position {idx} at zoom {zoom_level}: {str(e)}")
                        continue
                
                # Continue to next zoom level in steps list
                continue
            except Exception as e:
                print(f"Error processing zoom level {zoom_level}: {str(e)}")
                continue
    
    except Exception as e:
        print(f"Fatal error during capture: {str(e)}")
    finally:
        driver.quit()
        
        # Verify output size
        if verify_output_size(output_dir):
            print("Successfully captured visualization with required size ratio")
        else:
            print("Warning: Output size does not meet 10x-100x requirement")

if __name__ == '__main__':
    capture_visualization()
