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
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
