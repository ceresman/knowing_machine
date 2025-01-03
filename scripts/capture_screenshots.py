import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Coordinate system bounds from analysis
X_MIN, X_MAX = 788, 158465
Y_MIN, Y_MAX = 2067.23, 15742.12
ZOOM_LEVEL = 14.8544

# Viewport dimensions (based on browser window size)
VIEWPORT_WIDTH = 1504
VIEWPORT_HEIGHT = 869

# Calculate step sizes with 25% overlap
X_STEP = int(VIEWPORT_WIDTH * 0.75)  # 75% of viewport width for 25% overlap
Y_STEP = int(VIEWPORT_HEIGHT * 0.75)  # 75% of viewport height for 25% overlap

# Corner viewports for verification
CORNER_VIEWPORTS = [
    # Format: (x, y, zoom, description)
    (156900.14, 2793.01, 14.8544, "rightdown"),
    (4079.86, 14209.55, 14.8544, "leftup"),
]

# Output directory for screenshots
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def setup_driver():
    """Set up Chrome driver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument(f"--window-size={VIEWPORT_WIDTH},{VIEWPORT_HEIGHT}")  # Set exact viewport size
    chrome_options.add_argument("--hide-scrollbars")  # Hide scrollbars
    chrome_options.add_argument("--force-device-scale-factor=1")  # Ensure 1:1 pixel ratio
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def capture_screenshot(driver, x, y, zoom, description):
    """Capture screenshot at specified coordinates and zoom level."""
    url = f"https://calculatingempires.net/?pos={x},{y},{zoom}"
    driver.get(url)
    
    # Wait for the visualization to load
    time.sleep(5)  # Allow time for rendering
    
    # Generate filename
    filename = f"viewport_{description}_x{x}_y{y}_z{zoom}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Capture screenshot
    driver.save_screenshot(filepath)
    print(f"Captured screenshot: {filename}")
    return filepath

def main():
    """Main function to capture all required screenshots."""
    driver = setup_driver()
    
    try:
        # Calculate number of steps needed
        x_steps = int((X_MAX - X_MIN) / (VIEWPORT_WIDTH * 0.75)) + 1
        y_steps = int((Y_MAX - Y_MIN) / (VIEWPORT_HEIGHT * 0.75)) + 1
        
        print(f"Starting systematic capture: {x_steps}x{y_steps} grid")
        
        # Capture screenshots with systematic coverage
        index = 0
        for i in range(x_steps):
            x = X_MIN + (i * X_STEP)
            for j in range(y_steps):
                y = Y_MIN + (j * Y_STEP)
                filepath = capture_screenshot(driver, x, y, ZOOM_LEVEL, f"grid_{i}_{j}")
                print(f"Captured grid position ({i},{j}) at {filepath}")
                time.sleep(1)  # Prevent overwhelming the server
                index += 1
        
        # Capture the specific corner positions for verification
        print("\nCapturing corner viewports for verification...")
        for x, y, zoom, desc in CORNER_VIEWPORTS:
            filepath = capture_screenshot(driver, x, y, zoom, f"corner_{desc}")
            print(f"Captured corner viewport: {filepath}")
            time.sleep(1)
            
        print(f"\nCapture complete. Total screenshots: {index + len(CORNER_VIEWPORTS)}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
