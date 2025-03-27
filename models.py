from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Job:
    id: str
    title: str
    description: str
    url: str
    budget: float
    skills: List[str]
    proposals: str

@dataclass
class Proposal:
    job_id: str
    cover_letter: str
    status: str
    feedback: Optional[str]