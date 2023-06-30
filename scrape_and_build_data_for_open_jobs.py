from bs4 import BeautifulSoup as soup
from csv import writer

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

import config.user_config
import config.constants
from login_to_linkedin import login
from definitions import driver

HREF: str = "href"


def form_correct_search_url(incomplete_search_url, company_id):
    # Form correct search URL
    search_url = incomplete_search_url \
        .replace('__COMPANY_ID__', f'"{company_id}"') \
        .replace('__SEARCH_KEYWORD__', config.user_config.search_people_query)
    return search_url


def extract_user_details(search_url) -> list[dict[str, str]]:
    all_users_extracted_data = []

    print("Reading Content on 1st Page")
    driver.get(search_url)
    html_parser = soup(driver.page_source, "html.parser")
    first_page_user_details = extract_user_details_from_all_user_sections_on_this_page(html_parser)
    all_users_extracted_data.extend(first_page_user_details)

    # Go to second page and do the same
    try:
        print("Trying to read content on 2nd Page")
        next_button = driver.find_element(By.CLASS_NAME, "artdeco-pagination__button--next")
        print("Clicking Next Button")
        next_button.click()
        driver.implicitly_wait(30)

        html_parser = soup(driver.page_source, "html.parser")
        second_page_user_details = extract_user_details_from_all_user_sections_on_this_page(html_parser)
        all_users_extracted_data.extend(second_page_user_details)
    except NoSuchElementException:
        print("2nd Page was not present")

    return all_users_extracted_data


def extract_user_details_from_all_user_sections_on_this_page(html_parser) -> list[dict[str, str]]:
    all_users_extracted_data_on_this_page = []
    all_user_sections = html_parser.find_all("li", {"class": "reusable-search__result-container"})
    for user_section in all_user_sections:
        try:
            name = user_section.find("div", {"class": "display-flex align-items-center"}).img['alt']
        except:
            name = user_section.find("span", {"class": "entity-result__title-text t-16"}).a.text

        name = name.replace("\n", "").replace(",", "|").strip(" ")

        profile_links = user_section.find("div", {"class": "display-flex align-items-center"}).a['href']
        profile_links = profile_links.replace("\n", "").replace(",", "|")

        this_users_data = {"name": name, "profile": profile_links}
        all_users_extracted_data_on_this_page.append(this_users_data)

    return all_users_extracted_data_on_this_page


def get_list_of_users_with_details(company_name: str, company_id: str) -> list[dict[str, str]]:
    all_user = []
    # We will return a list of users where firstly we would have 1st level connections
    # then we will have 2nd connection and then 3rd connection

    if config.user_config.message_to_1st_connections:
        search_url = form_correct_search_url(config.constants.search_uri_for_1st_level_connections, company_id)
        _1st_connection_users = extract_user_details(search_url)
        all_user.extend(_1st_connection_users)
        print_users_of_connection(_1st_connection_users, company_name, '2nd')

    if config.user_config.message_to_2nd_connections:
        search_url = form_correct_search_url(config.constants.search_uri_for_2nd_level_connections, company_id)
        _2nd_connection_users = extract_user_details(search_url)
        all_user.extend(_2nd_connection_users)
        print_users_of_connection(_2nd_connection_users, company_name, '2nd')

    if config.user_config.message_for_3rd_connection:
        search_url = form_correct_search_url(config.constants.search_uri_for_3rd_level_connections, company_id)
        _3rd_connection_users = extract_user_details(search_url)
        all_user.extend(_3rd_connection_users)
        print_users_of_connection(_3rd_connection_users, company_name, '3rd')

    return all_user


def print_users_of_connection(connection_users, company_name, connection_number):
    print(f"\n{connection_number} Connection for Company - ", company_name)
    for user in connection_users:
        print(user)


def find_people_for_referrals(open_job_links):
    print("\n----- Finding People for Referral based on Open Jobs -----")
    company_id_2_job_link_map = get_company_id_2_job_link_mapping(open_job_links)

    for company_details, job_links in company_id_2_job_link_map.items():
        company_id, company_name = company_details
        list_of_users_with_details: list[dict[str, str]] = get_list_of_users_with_details(company_name, company_id)
        # company_id, company_name = company_details
        print(f"Messaging People for company {str.upper(company_name)}")

        for i in range(0, config.NUMBER_OF_PEOPLE_TO_MESSAGE_OF_A_COMPANY):
            this_user: dict[str, str] = list_of_users_with_details[i]
            # {"name": name, "profile": profile_links}
            print(f"\n{i}. Messaging {this_user['name']}")
            pass

        pass

    print("MAP VALUES")
    print(company_id_2_job_link_map)

    # create and open file to write.
    filename = "names_and_positions.csv"
    file = open(filename, 'a')
    writer_object = writer(file)

    # write the file header
    file_headers = ["Name", "ProfileLinks", "current_designation", "current_location"]
    writer_object.writerow(file_headers)

    # open_job_links = job_openings_list
    pass


if __name__ == '__main__':
    login()
    # create a database
    find_people_for_referrals(config.open_job_links)
