from selenium.common import ElementNotVisibleException, ElementNotSelectableException

from chrome_driver import driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

import config
import random
from config import *


def login():
    print(" ----- Initiating Login ----")

    linkedin_url = "https://www.linkedin.com"
    print("Opening Linkedin @ [", linkedin_url, "] \t<<<<")
    driver.get(linkedin_url)
    wait = WebDriverWait(
        driver, 20, poll_frequency=1,
        ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
    )
    # driver.implicitly_wait(random.randint(RAND_TIME_START, RAND_TIME_END))

    username = driver.find_element(By.ID, "session_key")
    print("Using Username: ", config.username)
    username.send_keys(config.username)

    password = driver.find_element(By.ID, "session_password")
    print("Using Password: ", config.password)
    password.send_keys(config.password)

    submit_button = driver.find_element(By.CLASS_NAME, "sign-in-form__submit-btn--full-width")
    print("Clicking Submit Button")
    submit_button.click()

    print(" ----- Login Done ----")
