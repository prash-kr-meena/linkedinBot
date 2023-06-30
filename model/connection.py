from __future__ import annotations


class Connection:
    connection_link: str  # Primary Key
    connection_name: str
    company_id: str
    last_message_time: str

    def __init__(self, connection_link: str, connection_name: str, company_id: str) -> None:
        self.connection_link = connection_link
        self.connection_name = connection_name
        self.company_id = company_id
