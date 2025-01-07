import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def test_browser():
    print("\nTesting basic browser functionality...")
    
    # Setup Chrome options
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    try:
        print("Initializing Chrome webdriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Setting window size...")
        driver.set_window_size(1024, 768)
        size = driver.get_window_size()
        print(f"Window size set to: {size['width']}x{size['height']}")
        
        print("\nTesting page load...")
        driver.get('https://example.com')
        print(f"Page title: {driver.title}")
        
        print("\nTesting JavaScript execution...")
        js_result = driver.execute_script('return document.readyState')
        print(f"Page ready state: {js_result}")
        
        print("\nAll basic browser tests passed!")
        return True
        
    except Exception as e:
        print(f"\nBrowser test failed: {str(e)}")
        return False
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == '__main__':
    test_browser()
