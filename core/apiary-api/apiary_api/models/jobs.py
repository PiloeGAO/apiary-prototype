"""List of all the available models used by the API.

To support the openapi.json correctly,
we need to apply this fixes:
https://github.com/pydantic/pydantic/issues/6647#issuecomment-1670232073
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

class RunCreateModel(BaseModel):
    """Base model for runs creation."""
    worker_id: Optional[int]
    command: Optional[str]
    log: list[str] | SkipJsonSchema[None] = Field(default=[], json_schema_extra=lambda x: x.pop("default"))
    date: Optional[str] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status: Optional[int] = 0
    metadata: Optional[dict] = {}

class RunEditModel(RunCreateModel):
    """Base model for run edition."""
    worker_id: Optional[int] = None
    command: Optional[str] = ""

class RunModel(RunEditModel):
    """Run display model."""
    id: str = ""

class TaskCreateModel(BaseModel):
    """Base model for tasks creation."""
    name: str
    command: str
    status: Optional[int] = 0
    parents: list[str] | SkipJsonSchema[None] = Field(default=[], json_schema_extra=lambda x: x.pop("default"))
    tags: list[str] | SkipJsonSchema[None] = Field(default=[], json_schema_extra=lambda x: x.pop("default"))
    metadata: Optional[dict] = {}

class TaskEditModel(TaskCreateModel):
    """Base model for tasks edition."""
    name: Optional[str] = None
    command: Optional[str] = None
    runs: list[RunModel] | SkipJsonSchema[None] = Field(default=[], json_schema_extra=lambda x: x.pop("default"))

class TaskModel(TaskEditModel):
    """Task display model."""
    id: str = ""

class JobCreateModel(BaseModel):
    """Base model for jobs creation."""
    name: str
    user_id: Optional[int] = 0
    status: Optional[int] = 0
    priority: Optional[int] = 500
    pools: list[str] | SkipJsonSchema[None] = Field(default=[], json_schema_extra=lambda x: x.pop("default"))
    tasks: list[TaskCreateModel] | SkipJsonSchema[None] = Field(default=[], json_schema_extra=lambda x: x.pop("default"))
    tags: list[str] | SkipJsonSchema[None] = Field(default=[], json_schema_extra=lambda x: x.pop("default"))
    metadata: Optional[dict] = {}

class JobEditModel(JobCreateModel):
    """Base model for jobs edition."""
    name: Optional[str] = None

class JobModel(JobEditModel):
    """Job display model."""
    id: str = ""
    pools: list[str] = []
    tasks: list[str] = []
    tags: list[str] = []
