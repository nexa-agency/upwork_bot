from typing import List
from models import Job


def filter_jobs(jobs: List[Job], keywords: List[str], min_budget: float) -> List[Job]:
    """
    Filters jobs based on keywords and minimum budget.
    """
    filtered_jobs = []
    for job in jobs:
        if (
            any(keyword.lower() in job.description.lower() for keyword in keywords)
            and job.budget >= min_budget
        ):
            filtered_jobs.append(job)
    return filtered_jobs
