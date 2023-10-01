import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# This file is required to be in the root of the project

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root...
print('ROOT_DIR - ', ROOT_DIR)

# --------------------------------------------------------

options = Options()
options.add_experimental_option("detach", True)  # This is to not close the Chrome Tab after script completion

# Options so that chrome can't detect if it is being controlled via selenium
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Scripts :  so that chrome can't detect if it is being controlled via selenium
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
# Rotating the user-agent through execute_cdp_cmd() command as follows:
driver.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
