# from urllib import parse
#
# from bs4 import BeautifulSoup as soup
# from selenium.common import ElementNotVisibleException, ElementNotSelectableException
# from selenium.webdriver.support.wait import WebDriverWait
#
# from chrome_driver import driver
#
# HREF: str = "href"
#
#
# def get_company_id_2_job_link_mapping(open_job_links) -> dict[(str, str), list[str]]:
#     # for handling case where multiple job openings are from 1 company only, we create a map
#     company_id_2_job_link_map: dict[(str, str), list[str]] = {}
#
#     for job_link in open_job_links:
#         company_link: str = __get_company_link_from_job_opening_page(job_link)
#         company_id, company_name = __get_company_details_from_company_page(company_link)
#
#         print(f"{company_name} : {company_id} ---> {job_link}")
#         company_detail = (company_id, company_name)
#
#         if company_detail in company_id_2_job_link_map:
#             (company_id_2_job_link_map[company_detail]).append(job_link)
#         else:
#             company_id_2_job_link_map[company_detail] = [job_link]
#
#     print("Company Details To Job Links - MAP")
#     print(company_id_2_job_link_map)
#     return company_id_2_job_link_map
#
#
# def __get_company_link_from_job_opening_page(job_link: str) -> str:
#     print("\nOpening Job Link [", job_link, "] \t<<<<")
#     driver.get(job_link)
#     WebDriverWait(
#         driver, 20, poll_frequency=1,
#         ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
#     )
#
#     # Selecting the HTML Element    -   Where it shows the company name on the UI
#     htmlParser = soup(driver.page_source, "html.parser")
#     all_anchor_on_job_page = htmlParser.find_all("a")
#     company_uri = None
#     for anchor in all_anchor_on_job_page:
#         if "/company/" in anchor[HREF]:
#             company_uri = anchor[HREF]
#             print(company_uri, "  <<-- Found The URI,\t Validate!!")
#             break
#     if company_uri is None:
#         raise Exception("Company Link Not Found!!")
#
#     if 'http' in company_uri:
#         return company_uri
#     else:
#         return "https://www.linkedin.com/" + company_uri
#
#
# def __get_company_details_from_company_page(company_link: str) -> tuple[str, str]:
#     # figure out the name and id of the company
#     print("\nOpening Company Link [", company_link, "] \t<<<<")
#     driver.get(company_link)
#     WebDriverWait(
#         driver, 20, poll_frequency=1,
#         ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
#     )
#
#     html_parser = soup(driver.page_source, "html.parser")
#     company_title = __extract_company_title(html_parser)
#     company_id = __extract_company_id(html_parser)
#     return company_id, company_title
#
#
# def __extract_company_title(html_parser) -> str:
#     # Selecting the HTML Element    -   Where it shows the company name
#     company_title = html_parser.find("h1", {"class": "org-top-card-summary__title"}).span.text
#     return company_title
#
#
# def __extract_company_id(html_parser) -> str:
#     # Selecting the HTML Element    -   Where it shows the number of employees
#     #
#     # <a href="/search/results/people/?currentCompany=%5B%2270996414%22%5D&amp;origin=COMPANY_PAGE_CANNED_SEARCH"
#     #    id="ember29"
#     #    class="ember-view org-top-card-summary-info-list__info-item"
#     # >
#     #     <span class="t-normal t-black--light link-without-visited-state link-without-hover-state">22 employees</span>
#     # </a>
#     #
#     all_anchor_on_job_page = html_parser.find_all("a", {"class": "org-top-card-summary-info-list__info-item"})
#
#     # out of the tags find the one whose href contains the string "/search/results/people/?"
#     for anchor_tag in all_anchor_on_job_page:
#         # After decoding the uri href would look like :
#         # https://www.linkedin.com/search/results/people/?currentCompany=["1441","16140","17876832","10440912","791962"]&origin=COMPANY_PAGE_CANNED_SEARCH
#         # we need to get the attribute currentCompany's first element, here 1441 which is the company id for Google
#
#         # Pick the one in which the uri contains "currentCompany="
#         if "currentCompany=" in anchor_tag[HREF]:
#             uri_to_interpolate_company_id = anchor_tag[HREF]
#
#             query_param_map: dict = parse.parse_qs(parse.urlsplit(uri_to_interpolate_company_id).query)
#             # print(query_param_map["currentCompany"])
#             # check if this is null, that will be an invalid case
#             company_id = query_param_map["currentCompany"][0]  # first_value_of_the_current_company_query_param
#
#             # /search/results/people/?currentCompany=%5B%2270996414%22%5D&origin=COMPANY_PAGE_CANNED_SEARCH
#             # Parse this URI to get the url parameters value
#             # if you see the above uri, in decoded form
#             # currentCompany=["70996414"]&origin=COMPANY_PAGE_CANNED_SEARCH
#             # here value is of the form  ["70996414","3489348"], ie it is not a string, so we need to remove extra characters
#             # >> we could simply remove all non digit characters
#             #  or remove the  ", [ , ]  characters
#
#             # sanitizing company id
#             company_id = company_id.replace('"', '')
#             company_id = company_id.replace('[', '')
#             company_id = company_id.replace(']', '')
#             # After removing this --> 70996414,3489348
#             company_id_list = str.split(company_id, ",")
#
#             # print("Company ID: ", company_id_list[0])
#             return company_id_list[0]
#
#     # If did not find company id -- Terminate
#     raise Exception("Company Id Not Found")
