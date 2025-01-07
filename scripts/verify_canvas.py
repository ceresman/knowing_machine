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
                driver.get('https://calculatingempires.net/')
                
                # Wait for initial page load
                time.sleep(5)
                
                # Wait for canvas presence with increased timeout
                canvas = WebDriverWait(driver, 30).until(
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
                                
                                // Log current properties for debugging
                                console.log('Current canvas properties:', JSON.stringify(props, null, 2));
                                
                                // Check if properties are within acceptable ranges
                                const dimensionsMatch = Math.abs(props.dimensions.width - 1976) < 10 && 
                                                      Math.abs(props.dimensions.height - 2114) < 10;
                                                      
                                const transformMatch = props.transform.computed.startsWith('matrix(') &&
                                                     props.transform.computed.includes('0.5') &&
                                                     props.transform.computed.includes('0, 0');
                                
                                if (dimensionsMatch && transformMatch) {
                                    console.log('Found correct canvas properties!');
                                    resolve(props);
                                } else {
                                    console.log('Canvas properties not yet stabilized. Retrying...');
                                    setTimeout(checkCanvas, 1000);
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

if __name__ == '__main__':
    success = verify_canvas_properties()
    sys.exit(0 if success else 1)
