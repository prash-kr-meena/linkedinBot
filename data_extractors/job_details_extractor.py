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
        job_title = None
        try:
            title_from_h1 = html_parser.find("h1", {"class": "job-details-jobs-unified-top-card__job-title"})
            title_from_div = html_parser.find("div", {"class": "job-details-jobs-unified-top-card__job-title"})
            if title_from_h1 is not None:
                job_title = title_from_h1.text.strip()
            else:
                job_title = title_from_div.text.strip()
        except:
            print("Error while parsing for Job title")
            pass

        job = Job(job_link, job_title)
        extracted_jobs.append(job)

        print(job.job_title.ljust(50, '`'), job.job_link.ljust(50, ' '))
    return extracted_jobs


if __name__ == '__main__':
    login()
    jobs = extract_jobs_details(open_job_links)
