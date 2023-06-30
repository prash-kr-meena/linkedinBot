from __future__ import annotations


class Company:
    company_id: str
    company_name: str
    company_link: str

    def __init__(self, company_id: str, company_name: str, company_link: str) -> None:
        self.company_id = company_id
        self.company_name = company_name
        self.company_link = company_link
