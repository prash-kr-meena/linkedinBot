from __future__ import annotations


class Job:
    job_link: str  # Primary Key
    job_title: str
    referral_submitted: int

    def __init__(self, job_link: str, job_title: str, referral_submitted: int = 0) -> None:
        self.job_link = job_link
        self.job_title = job_title
        self.referral_submitted = referral_submitted
