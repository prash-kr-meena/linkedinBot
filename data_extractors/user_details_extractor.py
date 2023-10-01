from bs4 import BeautifulSoup as soup
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from config import constants, user_config
from definitions import driver
from login_to_linkedin import login
from model.company import Company
from model.connection import Connection
from repository.referral_repository import find_all_companies


def __build_connection_search_url(incomplete_search_url, company_id):
    search_url = incomplete_search_url \
        .replace('__COMPANY_ID__', f'"{company_id}"') \
        .replace('__SEARCH_KEYWORD__', user_config.search_people_query)
    return search_url


def __extract_connection_details_from_page(html_parser, company: Company, level: int) -> list[Connection]:
    all_extracted_connections: list[Connection] = []  # List of all connections present on this page
    all_user_sections = html_parser.find_all("li", {"class": "reusable-search__result-container"})
    for user_section in all_user_sections:
        # extract connection names
        try:
            name = user_section.find("div", {"class": "display-flex align-items-center"}).img['alt']
        except:
            name = user_section.find("span", {"class": "entity-result__title-text t-16"}).a.text
        name = name.replace("\n", "").replace(",", "|").strip(" ")

        # extract connection profile
        profile_link = user_section.find("div", {"class": "display-flex align-items-center"}).a['href']
        profile_link = profile_link.replace("\n", "").replace(",", "|")

        if 'search' in profile_link or 'LinkedIn Member' in name:
            # We don't want to save this connection's data as it is not useful, and proceed further
            print(f"-> Connection Data Not Useful, build your network!")
            continue

        connection = Connection(profile_link, name, company.company_id, level)
        print(f"-> {connection.connection_name}")
        all_extracted_connections.append(connection)

    return all_extracted_connections


def extract_connection_details(company: Company, templated_search_url: str, level: int) -> list[Connection]:
    all_connections = []
    print(f"\nlevel {level} connection @ {company.company_name} \t 1st Page")

    search_url = __build_connection_search_url(templated_search_url, company.company_id)
    driver.get(search_url)

    html_parser = soup(driver.page_source, "html.parser")
    connections_on_first_page = __extract_connection_details_from_page(html_parser, company, level)
    all_connections.extend(connections_on_first_page)

    try:
        # Trying to read content on 2nd Page
        next_button = driver.find_element(By.CLASS_NAME, "artdeco-pagination__button--next")
        print("Clicking Next Button")
        next_button.click()
        driver.implicitly_wait(30)

        print(f"{level} connection @ {company.company_name} \t 2nd Page")
        html_parser = soup(driver.page_source, "html.parser")
        connections_on_second_page = __extract_connection_details_from_page(html_parser, company, level)
        all_connections.extend(connections_on_second_page)
    except NoSuchElementException:
        print("2nd Page was not present")
        pass

    print()
    return all_connections


def extract_1st_connections_details(company: Company) -> list[Connection]:
    return extract_connection_details(
        company,
        constants.search_uri_for_1st_level_connections,
        constants.first_level
    )


def extract_2nd_connections_details(company: Company) -> list[Connection]:
    return extract_connection_details(
        company,
        constants.search_uri_for_2nd_level_connections,
        constants.second_level
    )


def extract_3rd_connections_details(company: Company) -> list[Connection]:
    return extract_connection_details(
        company,
        constants.search_uri_for_3rd_level_connections,
        constants.third_level
    )


if __name__ == '__main__':
    login()
    companies: list[Company] = find_all_companies()
    for company in companies:
        connections = [
            extract_1st_connections_details(company),
            extract_2nd_connections_details(company),
            extract_3rd_connections_details(company)
        ]
        print(connections)
