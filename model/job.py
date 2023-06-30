from __future__ import annotations


class Job:
    job_title: str
    job_link: str
    referral_submitted: int

    def __init__(self, job_title: str, job_link: str, referral_submitted: int = 0) -> None:
        self.job_title = job_title
        self.job_link = job_link
        self.referral_submitted = referral_submitted
