from selenium.common import ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.support.wait import WebDriverWait

from bs4 import BeautifulSoup as soup
from definitions import driver
from config.user_config import open_job_links
from login_to_linkedin import login
from model.job import Job


def extract_jobs_details(open_job_links: list[str]) -> list[Job]:
    extracted_jobs = []

    print("-------------- Job Details --------------")
    print("Job Title".ljust(50, ' '), "Job Links".ljust(50, ' '))

    for job_link in open_job_links:
        driver.get(job_link)
        WebDriverWait(
            driver, 1000, poll_frequency=1,
            ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException]
        )
        # Selecting the HTML Element - H1 with the given class
        html_parser = soup(driver.page_source, "html.parser")
        job_title = html_parser.find("h1", {"class": "jobs-unified-top-card__job-title"}).text.strip()
        job = Job(job_title, job_link)
        extracted_jobs.append(job)

        print(job.job_title.ljust(50, '`'), job.job_link.ljust(50, ' '))
    return extracted_jobs


if __name__ == '__main__':
    login()
    jobs = extract_jobs_details(open_job_links)
