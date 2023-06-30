from data_extractors.user_details_extractor import extract_1st_connections_details, extract_2nd_connections_details, \
    extract_3rd_connections_details
from login_to_linkedin import login
from model.company import Company
from repository.repository import find_all_companies, persist_connections


def find_and_persist_people_for_asking_referral():
    print("\n\n----- Finding People for Referral based on Open Jobs -----")

    companies: list[Company] = find_all_companies()
    for company in companies:
        first_level_connections = extract_1st_connections_details(company)
        persist_connections(first_level_connections)

        second_level_connections = extract_2nd_connections_details(company)
        persist_connections(second_level_connections)

        third_level_connections = extract_3rd_connections_details(company)
        persist_connections(third_level_connections)


if __name__ == '__main__':
    login()
    find_and_persist_people_for_asking_referral()
