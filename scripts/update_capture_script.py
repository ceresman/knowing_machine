import sys
from pathlib import Path

def update_capture_script():
    script_path = Path('scripts/capture_screenshots.py')
    content = script_path.read_text()
    
    # Update imports and webdriver setup
    new_content = content.replace(
        'from selenium import webdriver',
        'from selenium import webdriver\nfrom webdriver_manager.chrome import ChromeDriverManager\nfrom selenium.webdriver.chrome.service import Service'
    ).replace(
        'return webdriver.Chrome(options=chrome_options)',
        'return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)'
    ).replace(
        '--window-size=1920,1080',
        '--window-size=3840,2160'  # 4K resolution
    )
    
    script_path.write_text(new_content)
    print("Successfully updated capture_screenshots.py")

if __name__ == "__main__":
    update_capture_script()
