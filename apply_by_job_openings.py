from bs4 import BeautifulSoup as soup
from csv import writer
from login import login
from chrome_driver import driver
import random
# from selenium.webdriver.common.by import By
from config import *
from urllib import parse

HREF: str = "href"


def get_company_link_from_job_opening_page(page_source: str) -> str:
    # Selecting the HTML Element    -   Where it shows the company name on the UI
    htmlParser = soup(page_source, "html.parser")
    all_anchor_on_job_page = htmlParser.find_all("a")
    second_half_company_uri = None
    for anchor in all_anchor_on_job_page:
        if "/company/" in anchor[HREF]:
            second_half_company_uri = anchor[HREF]
            print(second_half_company_uri, "  <<-- Found The URI,\t Validate!!")
            break
    company_link = "https://www.linkedin.com/" + second_half_company_uri
    return company_link


def apply_by_job_openings(open_job_links):
    print("----- Applying Referral based on Job Openings -----")

    # figure out the name and id of the company
    for job_link in open_job_links:
        print("Opening Job Link [", job_link, "] \t<<<<")
        driver.get(job_link)
        driver.implicitly_wait(random.randint(RAND_TIME_START, RAND_TIME_END))
        company_link: str = get_company_link_from_job_opening_page(driver.page_source)

        # -------------
        print("Opening Company Link [", company_link, "] \t<<<<")
        driver.get(company_link)
        driver.implicitly_wait(random.randint(RAND_TIME_START, RAND_TIME_END))

        # Selecting the HTML Element    -   Where it shows the number of employees
        #
        # <a href="/search/results/people/?currentCompany=%5B%2270996414%22%5D&amp;origin=COMPANY_PAGE_CANNED_SEARCH"
        #    id="ember29"
        #    class="ember-view org-top-card-summary-info-list__info-item"
        # >
        #     <span class="t-normal t-black--light link-without-visited-state link-without-hover-state">22 employees</span>
        # </a>
        #

        src = driver.page_source
        htmlParser = soup(src, "html.parser")
        all_anchor_on_job_page = htmlParser.find_all("a", {"class": "org-top-card-summary-info-list__info-item"})

        # out of the tags find the one whose href contains the string "/search/results/people/?"
        for anchor_tag in all_anchor_on_job_page:
            # After decoding the uri href would look like :
            # https://www.linkedin.com/search/results/people/?currentCompany=["1441","16140","17876832","10440912","791962"]&origin=COMPANY_PAGE_CANNED_SEARCH
            # we need to get the attribute currentCompany's first element, here 1441 which is the company id for Google

            # Pick the one in which the uri contains "currentCompany="
            if "currentCompany=" in anchor_tag[HREF]:
                uri_to_interpolate_company_id = anchor_tag[HREF]

                query_param_map: dict = parse.parse_qs(parse.urlsplit(uri_to_interpolate_company_id).query)
                print(query_param_map)
                print(query_param_map["currentCompany"])
                # check if this is null, that will be an invalid case
                company_id = query_param_map["currentCompany"][0]  # first_value_of_the_current_company_query_param

                # /search/results/people/?currentCompany=%5B%2270996414%22%5D&origin=COMPANY_PAGE_CANNED_SEARCH
                # if you see the above uri, in decoded form
                # currentCompany=["70996414"]&origin=COMPANY_PAGE_CANNED_SEARCH
                # the value is of the form  ["70996414"], ie it is not a string, so we would require to remove those extra characters
                # >> we could simply remove all non digit characters
                #  or remove the  ", [ , ]  characters

                # sanitizing company id
                company_id = company_id.replace('"', '')
                company_id = company_id.replace('[', '')
                company_id = company_id.replace(']', '')
                print("Company ID: ", company_id)

                # /search/results/people/?currentCompany=%5B%2270996414%22%5D&origin=COMPANY_PAGE_CANNED_SEARCH
                # Parse this URI to get the url parameters value
            break

            # check if link is string and contains the above string
            # if no  continue
            # if yes then parse this uri, using some library
            # and extract out the attribute value
            # make sure to save this id and terminate the loop here
            # will porcess the id later

        pass

    # create and open file to write
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
    apply_by_job_openings(open_job_links)
