import os
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Define the viewport coordinates and zoom levels
VIEWPORTS = [
    # Format: (x, y, zoom, description)
    (156900.14, 2793.01, 14.8544, "rightdown"),
    (4079.86, 14209.55, 14.8544, "leftup"),
]

ZOOM_LEVELS = [14.8544]  # Add more zoom levels if needed

# Output directory for screenshots
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def setup_driver():
    """Set up Chrome driver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--window-size=3840,2160")  # Set window size
    chrome_options.add_argument("--hide-scrollbars")  # Hide scrollbars
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
        # Capture screenshots for each viewport at specified zoom levels
        for x, y, zoom, desc in VIEWPORTS:
            filepath = capture_screenshot(driver, x, y, zoom, desc)
            print(f"Saved screenshot to: {filepath}")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
