RAND_TIME_START: int = 1
RAND_TIME_END: int = 10

search_uri_for_1st_level_connections: str = 'https://www.linkedin.com/search/results/people/?currentCompany=[__COMPANY_ID__]&keywords=__SEARCH_KEYWORD__&network=["F"]&origin=FACETED_SEARCH'
search_uri_for_2nd_level_connections: str = 'https://www.linkedin.com/search/results/people/?currentCompany=[__COMPANY_ID__]&keywords=__SEARCH_KEYWORD__&network=["S"]&origin=FACETED_SEARCH'
search_uri_for_3rd_level_connections: str = 'https://www.linkedin.com/search/results/people/?currentCompany=[__COMPANY_ID__]&keywords=__SEARCH_KEYWORD__&network=["O"]&origin=FACETED_SEARCH'

first_level: int = 1
second_level: int = 2
third_level: int = 3
