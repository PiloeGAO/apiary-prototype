"""List of all the available models used by the API."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class RunCreateModel(BaseModel):
    """Base model for runs creation."""
    worker_id: Optional[int]
    command: Optional[str]
    log: Optional[list[str]] = []
    date: Optional[str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status: Optional[int] = 0
    metadata: Optional[dict] = {}

class RunEditModel(RunCreateModel):
    """Base model for run edition."""
    worker_id: Optional[int] = None
    command: Optional[str] = ""

class TaskCreateModel(BaseModel):
    """Base model for tasks creation."""
    name: str
    command: str
    status: Optional[int] = 0
    parents: Optional[list[int]] = []
    tags: Optional[list[str]] = []
    metadata: Optional[dict] = {}

class TaskEditModel(TaskCreateModel):
    """Base model for tasks edition."""
    name: Optional[str] = None
    command: Optional[str] = None
    runs: Optional[str] = []

class JobCreateModel(BaseModel):
    """Base model for jobs creation."""
    name: str
    user_id: Optional[int] = 0
    status: Optional[int] = 0
    pools: Optional[list[int]] = []
    priority: Optional[int] = 500
    tasks: Optional[list[TaskCreateModel]] = []
    metadata: Optional[dict] = {}

class JobEditModel(JobCreateModel):
    """Base model for jobs edition."""
    name: Optional[str] = None
