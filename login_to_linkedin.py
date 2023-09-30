import random
import time
from bs4 import BeautifulSoup as soup

from selenium.common import JavascriptException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from config import user_config
from config.constants import RAND_TIME_START, RAND_TIME_END
from definitions import driver


def login():
    print("\n----- Initiating Login ----")

    linkedin_url = "https://www.linkedin.com"
    print("Opening Linkedin @ [", linkedin_url, "]")
    driver.get(linkedin_url)
    WebDriverWait(driver, 1000)
    driver.implicitly_wait(random.randint(RAND_TIME_START, RAND_TIME_END))
    time.sleep(5)

    try:
        # handle situations where we get the join-in form instead of login
        driver.execute_script("document.getElementsByClassName('flip-card')[0].classList.add('show-login');")
    except JavascriptException:
        pass

    html_parser = soup(driver.page_source, "html.parser")
    body = html_parser.find("body")
    while body.text == "":
        # Empty Body Page did not load properly, refresh
        driver.refresh()
        html_parser = soup(driver.page_source, "html.parser")
        body = html_parser.find("body")

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
