import random

from selenium.common import ElementNotVisibleException, ElementNotSelectableException

from definitions import driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from config import user_config
from config.user_config import RAND_TIME_START, RAND_TIME_END


def login():
    print("\n----- Initiating Login ----")

    linkedin_url = "https://www.linkedin.com"
    print("Opening Linkedin @ [", linkedin_url, "]")
    driver.get(linkedin_url)
    WebDriverWait(
        driver, 1000, poll_frequency=1,
        ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
    )
    driver.implicitly_wait(random.randint(RAND_TIME_START, RAND_TIME_END))

    username = driver.find_element(By.ID, "session_key")
    print("Using Username: ", user_config.username)
    username.send_keys(user_config.username)

    password = driver.find_element(By.ID, "session_password")
    print("Using Password: ", user_config.password)
    password.send_keys(user_config.password)

    submit_button = driver.find_element(By.CLASS_NAME, "sign-in-form__submit-btn--full-width")
    print("Clicking Submit Button")
    submit_button.click()

    print("----- Login Done ----\n\n")
