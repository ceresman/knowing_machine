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

def verify_canvas_properties(timeout=60):
    """Verify canvas dimensions and transform matrix with proper timeout."""
    print("\nVerifying canvas properties...")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=2500,2500')  # Larger window to ensure full canvas visibility
    options.add_argument('--disable-gpu')
    options.add_argument('--enable-logging')
    options.add_argument('--v=1')
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Navigating to page...")
        driver.get('https://calculatingempires.net/')
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Wait for canvas presence
                canvas = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "canvas"))
                )
                
                # Get canvas properties with detailed debugging
                props = driver.execute_script("""
                    return new Promise((resolve) => {
                        const checkCanvas = () => {
                            const canvas = document.querySelector('canvas');
                            if (!canvas) {
                                console.log('Canvas not found, retrying...');
                                setTimeout(checkCanvas, 500);
                                return;
                            }
                            
                            const style = window.getComputedStyle(canvas);
                            const map = window.map;
                            
                            // Force a resize event
                            window.dispatchEvent(new Event('resize'));
                            
                            // Wait for any animations
                            setTimeout(() => {
                                const props = {
                                    dimensions: {
                                        width: canvas.width,
                                        height: canvas.height,
                                        clientWidth: canvas.clientWidth,
                                        clientHeight: canvas.clientHeight,
                                        style: {
                                            width: style.width,
                                            height: style.height
                                        }
                                    },
                                    transform: {
                                        computed: style.transform,
                                        origin: style.transformOrigin,
                                        style: canvas.style.transform
                                    },
                                    map: {
                                        initialized: typeof map !== 'undefined',
                                        size: map ? map.getSize() : null,
                                        view: map ? {
                                            zoom: map.getView().getZoom(),
                                            center: map.getView().getCenter(),
                                            resolution: map.getView().getResolution()
                                        } : null
                                    },
                                    window: {
                                        innerWidth: window.innerWidth,
                                        innerHeight: window.innerHeight,
                                        devicePixelRatio: window.devicePixelRatio
                                    }
                                };
                                
                                if (props.dimensions.width === 1976 && 
                                    props.dimensions.height === 2114 && 
                                    props.transform.computed === 'matrix(0.5, 0, 0, 0.5, 0, 0)') {
                                    console.log('Found correct canvas properties!');
                                    resolve(props);
                                } else {
                                    console.log('Canvas properties not yet correct:', JSON.stringify(props, null, 2));
                                    setTimeout(checkCanvas, 500);
                                }
                            }, 1000);
                        };
                        
                        checkCanvas();
                    });
                """)
                
                print("\nCanvas Properties:")
                print(json.dumps(props, indent=2))
                
                # Verify dimensions
                if props['dimensions']['width'] != 1976 or props['dimensions']['height'] != 2114:
                    print("\n❌ Canvas dimensions incorrect:")
                    print(f"Expected: 1976x2114")
                    print(f"Got: {props['dimensions']['width']}x{props['dimensions']['height']}")
                    return False
                
                # Verify transform matrix
                expected_transform = "matrix(0.5, 0, 0, 0.5, 0, 0)"
                if props['transform']['computed'] != expected_transform:
                    print("\n❌ Transform matrix incorrect:")
                    print(f"Expected: {expected_transform}")
                    print(f"Got: {props['transform']['computed']}")
                    return False
                
                print("\n✅ Canvas properties verified successfully:")
                print(f"- Dimensions: {props['dimensions']['width']}x{props['dimensions']['height']}")
                print(f"- Transform: {props['transform']['computed']}")
                return True
                
            except Exception as e:
                remaining = timeout - (time.time() - start_time)
                if remaining <= 0:
                    print(f"\n❌ Timeout reached while verifying canvas properties: {str(e)}")
                    return False
                print(f"Retrying... {remaining:.1f}s remaining")
                time.sleep(1)
                
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == '__main__':
    success = verify_canvas_properties()
    sys.exit(0 if success else 1)
