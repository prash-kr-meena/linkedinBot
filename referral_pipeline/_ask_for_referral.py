import time
from typing import List

from bs4 import BeautifulSoup as soup
from selenium.common import ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

import config.user_config
from definitions import driver
from login_to_linkedin import login
from model.connection import Connection
from repository.referral_repository import find_all_connections
from repository.referral_repository import find_company_by_id
from repository.referral_repository import find_jobs_by_company_id


def templatize_message(message_to_connections: str, connection: Connection):
    message = message_to_connections
    # if connection name has only one word take it, if it has more than 2 words, take the first 2 only
    connection_name_words = connection.connection_name.split(" ")

    ideal_connection_name = ""
    if len(connection_name_words) == 1:
        ideal_connection_name = connection_name_words[0]
    elif len(connection_name_words) > 1:
        ideal_connection_name = connection_name_words[0] + " " + connection_name_words[1]

    ideal_connection_name = ideal_connection_name.lower().capitalize()
    message = message.replace("{name}", ideal_connection_name)

    company = find_company_by_id(connection.company_id)
    company_name = company.company_name if company is not None else "your organization"
    message = message.replace("{company_name}", company_name)

    jobs = find_jobs_by_company_id(connection.company_id)
    all_job_links = []
    for index, job in enumerate(jobs):
        all_job_links.append(str(index) + ".  " + job.job_link)
    all_job_links_message = "\n".join(all_job_links)
    message = message.replace("{job_links}", all_job_links_message)
    print(message)
    return message  # final message after templetizing


def find_connect_button_in_more_actions_drop_down(driver: driver) -> WebElement | None:
    # Find the "connect" button
    html_parser = soup(driver.page_source, "html.parser")
    button_divs = html_parser.find_all("div", {
        "role": "button",
        "class": "artdeco-dropdown__item artdeco-dropdown__item--is-dropdown ember-view full-width display-flex align-items-center"
    })
    connection_button_div = None
    for button_div in button_divs:
        button_label = button_div['aria-label'].lower()
        if "invite" in button_label and "connect" in button_label:
            connection_button_div = button_div  # we need the one from the last
    # print(connection_button_div)

    if connection_button_div is None:
        print("ERROR: Connection Button Not Found")
        print("Didn't Send Connection request to this user, Processing next user")
        return None

    actual_button = driver.find_element(By.ID, connection_button_div['id'])
    # print(actual_button)
    return actual_button


def find_connect_button_on_profile(driver: driver) -> WebElement | None:
    # Find the "connect" button on profile
    profile_buttons: List[WebElement] = driver.find_elements(By.CSS_SELECTOR, "div.pvs-profile-actions button")
    connect_button: WebElement = None
    for profile_button in profile_buttons:
        if profile_button.text == 'Connect':
            connect_button = profile_button
            break

    if connect_button is not None:
        return connect_button
    else:
        print("ERROR: Connection Button Not Found, on Profile Page")
        print("Didn't Send Connection request to this user, Processing next user")
        return None
    #
    # html_parser = soup(driver.page_source, "html.parser")
    # buttons_elements = html_parser.find_all("button")
    # correct_connection_button_element = None
    # for button_element in buttons_elements:
    #     if 'aria-label' not in button_element.attrs:
    #         continue
    #
    #     button_label = button_element['aria-label'].lower()
    #     if "invite" in button_label and "connect" in button_label:
    #         correct_connection_button_element = button_element  # we need the one from the last
    # # print(correct_connection_button_element)
    #
    # if correct_connection_button_element is None:
    #     print("ERROR: Connection Button Not Found, on Profile Page")
    #     print("Didn't Send Connection request to this user, Processing next user")
    #     return None
    #
    # actual_button = driver.find_element(By.ID, correct_connection_button_element['id'])
    # # print(actual_button)
    # return actual_button


def find_and_click_more_action_button_on_profile(driver: driver):
    html_parser = soup(driver.page_source, "html.parser")
    more_actions_button = html_parser.find_all("button", {"aria-label": "More actions"})
    action_button_id = more_actions_button[-1]['id']  # taking the id of the last element
    action_button = driver.find_element(By.ID, action_button_id)
    action_button.click()


def find_and_add_message_to_text_area(driver: driver, message: str):
    # Find the text area and add text to it
    html_parser = soup(driver.page_source, "html.parser")  # Read the Page again, as the new Popup is added
    text_area = driver.find_element(By.ID, "custom-message")
    text_area.send_keys(message)


def click_send_message_button(driver: driver):
    # Find the 'Send' Button and click it
    html_parser = soup(driver.page_source, "html.parser")  # Read the Page again, as the new Popup is added
    send_button = html_parser.find_all("button", {"aria-label": "Send now"})
    send_button_id = send_button[-1]['id']  # taking the id of the last element
    send_button = driver.find_element(By.ID, send_button_id)
    send_button.click()
    pass


def send_connection_request_with_a_note(connection: Connection):
    driver.get(connection.connection_link)
    WebDriverWait(
        driver, 1000, poll_frequency=1,
        ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
    )
    time.sleep(2)

    # Check if the connect button is present directly on the profile, if Yes then click it
    connect_button = find_connect_button_on_profile(driver)
    if connect_button is not None:
        connect_button.click()
    else:
        # Button not found on profile page check it under the "More Action" button
        # Find the "More Action" button - and clicking it
        find_and_click_more_action_button_on_profile(driver)

        # Find the "connect" button - and clicking it
        connect_button = find_connect_button_in_more_actions_drop_down(driver)
        if connect_button is not None:
            connect_button.click()
        else:
            print("ERROR: Connection Button Not Found for connection - ", connection.connection_name)
            print("Didn't Send Connection request to this user, Processing next user")
            return

    find_and_click_add_note_button(driver)

    if connection.connection_level == 2:
        message = templatize_message(config.user_config.referral_message_for_2nd_connection, connection)
    elif connection.connection_level == 3:
        message = templatize_message(config.user_config.referral_message_for_3rd_connection, connection)

    find_and_add_message_to_text_area(driver, message)
    click_send_message_button(driver)


def find_and_click_add_note_button(driver: driver):
    # Find the 'Add a note' Button and click it
    html_parser = soup(driver.page_source, "html.parser")  # Read the Page again, as the new Popup is added
    add_a_note_button = html_parser.find_all("button", {"aria-label": "Add a note"})
    add_a_note_button_id = add_a_note_button[-1]['id']  # taking the id of the last element
    add_a_note_button = driver.find_element(By.ID, add_a_note_button_id)
    add_a_note_button.click()


def directly_message_the_connection(connection: Connection):
    pass


def ask_for_referral():
    print("\n\n----- Messaging all the People for Referral, for the corresponding Jobs -----")
    all_connections = find_all_connections()
    for connection in all_connections:
        print(connection)
        if connection.connection_level == 1:
            directly_message_the_connection(connection)
        else:
            send_connection_request_with_a_note(connection)
    pass


if __name__ == '__main__':
    login()
    ask_for_referral()
