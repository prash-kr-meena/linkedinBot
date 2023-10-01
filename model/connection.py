from __future__ import annotations

import json


class Connection:
    connection_link: str  # Primary Key
    connection_name: str
    company_id: str
    connection_level: int
    last_message_time: str

    def __init__(
            self,
            connection_link: str,
            connection_name: str,
            company_id: str,
            connection_level: int,
            last_message_time: str = None
    ) -> None:
        self.connection_link = connection_link
        self.connection_name = connection_name
        self.company_id = company_id
        self.connection_level = connection_level
        self.last_message_time = last_message_time

    def __str__(self) -> str:
        return json.dumps(self.__dict__)
