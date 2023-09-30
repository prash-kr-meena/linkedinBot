from typing import Optional

from database.sqlitedb import TRowSet
from model.company import Company
from model.connection import Connection
from model.job import Job
from repository.db import dbm


def persist_job(job: Job, company: Company):
    print(f"Persisting Company '{company.company_name}' AND job '{job.job_title}'")

    job_in_db = find_job_by_id(job.job_link)
    if job_in_db is not None:
        print("Job already exists in DB")
        return

    persist_company(company)

    dbm.execute_nonquery(
        query="INSERT INTO job values (:job_link, :job_title, :referral_submitted, :company_id)",
        query_params={
            "job_link": job.job_link,
            "job_title": job.job_title,
            "referral_submitted": job.referral_submitted,
            "company_id": company.company_id
        }
    )
    dbm.commit()


def persist_company(company: Company):
    print(f"Persisting Company {company.company_name}")

    company_in_db = find_company_by_id(company.company_id)
    if company_in_db is not None:
        print("Company exists in DB, No persistence required")
        return

    dbm.execute_nonquery(
        query="INSERT INTO company values (:company_id, :company_name, :company_link)",
        query_params={
            "company_id": company.company_id,
            "company_name": company.company_name,
            "company_link": company.company_link
        }
    )
    dbm.commit()


def find_company_by_id(company_id: str) -> Optional[Company]:
    companies_iterator: TRowSet = dbm.fetch_rowset(
        query="SELECT * FROM company where company_id=:company_id",
        query_params={'company_id': company_id}
    )
    companies = list(companies_iterator)

    if len(companies) == 0:
        return None
    else:
        company_tuple = tuple(companies[0])
        company = Company(company_tuple[0], company_tuple[1], company_tuple[2])
        return company


def find_job_by_id(job_link: str) -> Optional[Job]:
    jobs_iterator: TRowSet = dbm.fetch_rowset(
        query="SELECT * FROM job where job_link=:job_link",
        query_params={'job_link': job_link}
    )
    jobs = list(jobs_iterator)

    if len(jobs) == 0:
        return None
    else:
        job_tuple = tuple(jobs[0])
        job = Job(job_tuple[0], job_tuple[1], job_tuple[2])
        return job


def find_all_companies() -> list[Company]:
    companies_iterator: TRowSet = dbm.fetch_rowset(query="SELECT * FROM company")
    companies = []
    for company_tuple in companies_iterator:
        company = Company(company_tuple[0], company_tuple[1], company_tuple[2])
        companies.append(company)
    return companies


def persist_connection(connection: Connection) -> None:
    print(f"Persisting Connection  '{connection.connection_name}'")
    dbm.execute_nonquery(
        query="INSERT INTO connection values (:connection_link, :connection_name, :company_id, :last_message_time)",
        query_params={
            "connection_link": connection.connection_link,
            "connection_name": connection.connection_name,
            "company_id": connection.company_id,
            "last_message_time": None
        }
    )
    dbm.commit()


def persist_connections(connections: list[Connection]) -> None:
    for connection in connections:
        persist_connection(connection)


def find_connection_by_id(connection_link: str):
    connection_iterator: TRowSet = dbm.fetch_rowset(
        query="SELECT * FROM connection where connection_link=:connection_link",
        query_params={'connection_link': connection_link}
    )
    connections = list(connection_iterator)

    if len(connections) == 0:
        return None
    else:
        connection_tuple = tuple(connections[0])
        connection = Connection(connection_tuple[0], connection_tuple[1], connection_tuple[2])
        return connection
