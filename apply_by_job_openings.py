from bs4 import BeautifulSoup as soup
from csv import writer

from selenium.common import ElementNotVisibleException, ElementNotSelectableException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from login import login
from chrome_driver import driver
import random
# from selenium.webdriver.common.by import By
from config import *
from urllib import parse

HREF: str = "href"


def get_company_link_from_job_opening_page(job_link: str) -> str:
    print("\nOpening Job Link [", job_link, "] \t<<<<")
    driver.get(job_link)
    WebDriverWait(
        driver, 20, poll_frequency=1,
        ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
    )

    # Selecting the HTML Element    -   Where it shows the company name on the UI
    htmlParser = soup(driver.page_source, "html.parser")
    all_anchor_on_job_page = htmlParser.find_all("a")
    company_uri = None
    for anchor in all_anchor_on_job_page:
        if "/company/" in anchor[HREF]:
            company_uri = anchor[HREF]
            print(company_uri, "  <<-- Found The URI,\t Validate!!")
            break
    if company_uri is None:
        raise Exception("Company Link Not Found!!")

    if 'http' in company_uri:
        return company_uri
    else:
        return "https://www.linkedin.com/" + company_uri


def extract_company_title(html_parser) -> str:
    # Selecting the HTML Element    -   Where it shows the company name
    company_title = html_parser.find("h1", {"class": "org-top-card-summary__title"}).span.text
    return company_title


def extract_company_id(html_parser) -> str:
    # Selecting the HTML Element    -   Where it shows the number of employees
    #
    # <a href="/search/results/people/?currentCompany=%5B%2270996414%22%5D&amp;origin=COMPANY_PAGE_CANNED_SEARCH"
    #    id="ember29"
    #    class="ember-view org-top-card-summary-info-list__info-item"
    # >
    #     <span class="t-normal t-black--light link-without-visited-state link-without-hover-state">22 employees</span>
    # </a>
    #
    all_anchor_on_job_page = html_parser.find_all("a", {"class": "org-top-card-summary-info-list__info-item"})

    # out of the tags find the one whose href contains the string "/search/results/people/?"
    for anchor_tag in all_anchor_on_job_page:
        # After decoding the uri href would look like :
        # https://www.linkedin.com/search/results/people/?currentCompany=["1441","16140","17876832","10440912","791962"]&origin=COMPANY_PAGE_CANNED_SEARCH
        # we need to get the attribute currentCompany's first element, here 1441 which is the company id for Google

        # Pick the one in which the uri contains "currentCompany="
        if "currentCompany=" in anchor_tag[HREF]:
            uri_to_interpolate_company_id = anchor_tag[HREF]

            query_param_map: dict = parse.parse_qs(parse.urlsplit(uri_to_interpolate_company_id).query)
            # print(query_param_map["currentCompany"])
            # check if this is null, that will be an invalid case
            company_id = query_param_map["currentCompany"][0]  # first_value_of_the_current_company_query_param

            # /search/results/people/?currentCompany=%5B%2270996414%22%5D&origin=COMPANY_PAGE_CANNED_SEARCH
            # Parse this URI to get the url parameters value
            # if you see the above uri, in decoded form
            # currentCompany=["70996414"]&origin=COMPANY_PAGE_CANNED_SEARCH
            # here value is of the form  ["70996414","3489348"], ie it is not a string, so we need to remove extra characters
            # >> we could simply remove all non digit characters
            #  or remove the  ", [ , ]  characters

            # sanitizing company id
            company_id = company_id.replace('"', '')
            company_id = company_id.replace('[', '')
            company_id = company_id.replace(']', '')
            # After removing this --> 70996414,3489348
            company_id_list = str.split(company_id, ",")

            # print("Company ID: ", company_id_list[0])
            return company_id_list[0]

    # If did not find company id -- Terminate
    raise Exception("Company Id Not Found")


def get_company_details_from_company_page(company_link: str) -> tuple[str, str]:
    # figure out the name and id of the company
    print("\nOpening Company Link [", company_link, "] \t<<<<")
    driver.get(company_link)
    WebDriverWait(
        driver, 20, poll_frequency=1,
        ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
    )

    html_parser = soup(driver.page_source, "html.parser")
    company_title = extract_company_title(html_parser)
    company_id = extract_company_id(html_parser)
    return company_id, company_title


def form_correct_search_url(incomplete_search_url, company_id):
    # Form correct search URL
    search_url = incomplete_search_url \
        .replace('__COMPANY_ID__', f'"{company_id}"') \
        .replace('__SEARCH_KEYWORD__', search_people_query)
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

    if message_to_1st_connections:
        search_url = form_correct_search_url(search_1st_connections, company_id)
        _1st_connection_users = extract_user_details(search_url)
        all_user.extend(_1st_connection_users)
        print_users_of_connection(_1st_connection_users, company_name, '2nd')

    if message_to_2nd_connections:
        search_url = form_correct_search_url(search_2nd_connections, company_id)
        _2nd_connection_users = extract_user_details(search_url)
        all_user.extend(_2nd_connection_users)
        print_users_of_connection(_2nd_connection_users, company_name, '2nd')

    if message_for_3rd_connection:
        search_url = form_correct_search_url(search_3rd_connections, company_id)
        _3rd_connection_users = extract_user_details(search_url)
        all_user.extend(_3rd_connection_users)
        print_users_of_connection(_3rd_connection_users, company_name, '3rd')

    return all_user


def print_users_of_connection(connection_users, company_name, connection_number):
    print(f"\n{connection_number} Connection for Company - ", company_name)
    for user in connection_users:
        print(user)


def apply_by_job_openings(open_job_links):
    print("\n----- Applying Referral based on Job Openings -----")
    company_id_2_job_link_map = get_company_id_2_job_link_mapping(open_job_links)

    for company_details, job_links in company_id_2_job_link_map.items():
        company_id, company_name = company_details
        list_of_users_with_details: list[dict[str, str]] = get_list_of_users_with_details(company_name, company_id)
        # company_id, company_name = company_details
        print(f"Messaging People for company {str.upper(company_name)}")

        for i in range(0, NUMBER_OF_PEOPLE_TO_MESSAGE_OF_A_COMPANY):
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


def get_company_id_2_job_link_mapping(open_job_links) -> dict[(str, str), list[str]]:
    # for handling case where multiple job openings are from 1 company only, we create a map
    company_id_2_job_link_map: dict[(str, str), list[str]] = {}
    for job_link in open_job_links:
        company_link: str = get_company_link_from_job_opening_page(job_link)
        company_id, company_name = get_company_details_from_company_page(company_link)

        print(f"{company_name} : {company_id} ---> {job_link}")
        company_detail = (company_id, company_name)

        if company_detail in company_id_2_job_link_map:
            (company_id_2_job_link_map[company_detail]).append(job_link)
        else:
            company_id_2_job_link_map[company_detail] = [job_link]

    print("Company Details To Job Links - MAP")
    print(company_id_2_job_link_map)
    return company_id_2_job_link_map


if __name__ == '__main__':
    login()
    apply_by_job_openings(open_job_links)
