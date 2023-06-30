import config.user_config
from data_extractors.company_details_extractor import extract_company_details
from data_extractors.job_details_extractor import extract_jobs_details
from login_to_linkedin import login
from config import user_config


def find_people_for_asking_referral(open_job_links: list[str]):
    jobs = extract_jobs_details(open_job_links)
    for job in jobs:
        companies = extract_company_details(job)
    pass


if __name__ == '__main__':
    login()
    find_people_for_asking_referral(user_config.open_job_links)
