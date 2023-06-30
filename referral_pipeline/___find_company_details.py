import config.user_config
from data_extractors.company_details_extractor import extract_company_details
from data_extractors.job_details_extractor import extract_jobs_details
from login_to_linkedin import login
from model.job import Job
from repository.repository import persist_job


def find_and_save_company_details(open_job_links: list[str]):
    jobs: list[Job] = extract_jobs_details(open_job_links)
    for job in jobs:
        company = extract_company_details(job)
        persist_job(job, company)


if __name__ == '__main__':
    login()
    find_and_save_company_details(config.user_config.open_job_links)
