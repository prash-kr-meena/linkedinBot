from selenium.common import ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.support.wait import WebDriverWait
from model.company import Company
from urllib import parse
from definitions import driver
from config.user_config import open_job_links
from data_extractors.job_details_extractor import extract_jobs_details
from login_to_linkedin import login
from model.job import Job
from bs4 import BeautifulSoup as soup

HREF: str = "href"


def __get_company_link_from_job_opening_page(job: Job) -> str:
    print(f"Opening Job '{job.job_title}' @ [", job.job_link, "]")
    driver.get(job.job_link)
    WebDriverWait(
        driver, 1000, poll_frequency=1,
        ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
    )

    # Selecting the HTML Element    -   Where it shows the company name on the UI
    html_parser = soup(driver.page_source, "html.parser")
    all_anchor_on_job_page = html_parser.find_all("a")

    company_uri = None
    for anchor in all_anchor_on_job_page:
        # handle cases where 'href' is not present in the anchor itself
        if 'href' in anchor.attrs and "/company/" in anchor[HREF]:
            company_uri = anchor[HREF]
            # print(company_uri, "  <<-- Found The URI,\t Validate!!")
            print("Company Link :", company_uri)
            break

    if company_uri is None:
        raise Exception("Company Link Not Found!!")

    if 'http' in company_uri:
        return company_uri
    else:
        return "https://www.linkedin.com/" + company_uri


def __get_company_details_from_company_page(company_link: str) -> Company:
    # figure out the name and id of the company
    print("Opening Company Link [", company_link, "]")
    driver.get(company_link)
    WebDriverWait(
        driver, 1000, poll_frequency=1,
        ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
    )

    html_parser = soup(driver.page_source, "html.parser")
    company_name = __extract_company_title(html_parser)
    company_id = __extract_company_id(html_parser)

    return Company(company_id, company_name, company_link)


def __extract_company_title(html_parser) -> str:
    # Selecting the HTML Element    -   Where it shows the company name
    company_title = html_parser.find("h1", {"class": "org-top-card-summary__title"}).span.text
    return company_title


def __extract_company_id(html_parser) -> str:
    # Selecting the HTML Element    -   Where it shows the number of employees

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


def extract_company_details(job: Job) -> Company:
    print("\n\n-------------- Company Details --------------")
    company_link: str = __get_company_link_from_job_opening_page(job)
    # if company details are available in db, get it from there instead of making network call
    company = __get_company_details_from_company_page(company_link)
    print(f"{company.company_name} [{company.company_id}] \t\t '{job.job_title}' @ [{job.job_link}]")
    return company


if __name__ == '__main__':
    login()
    jobs = extract_jobs_details(open_job_links)
    for job in jobs:
        companies = extract_company_details(job)
