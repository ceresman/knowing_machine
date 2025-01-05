#!/usr/bin/env python3
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def check_versions():
    print("Python version:", sys.version)
    print("Selenium version:", webdriver.__version__)
    
    try:
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        print("Chrome version:", driver.capabilities['browserVersion'])
        print("Chromedriver version:", driver.capabilities['chrome']['chromedriverVersion'])
        driver.quit()
    except Exception as e:
        print("Error initializing Chrome:", str(e))

if __name__ == "__main__":
    check_versions()
