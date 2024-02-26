"""List of all the available models used by the API.

To support the openapi.json correctly,
we need to apply this fixes:
https://github.com/pydantic/pydantic/issues/6647#issuecomment-1670232073
"""
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

class WorkersEditModel(BaseModel):
    """Base model for worker edition."""

    name: Optional[str]
    status: Optional[int] = 0
    pools: list[str] | SkipJsonSchema[None] = Field(
        default=[], json_schema_extra=lambda x: x.pop("default")
    )
    tags: list[str] | SkipJsonSchema[None] = Field(
        default=[], json_schema_extra=lambda x: x.pop("default")
    )
    metadata: Optional[dict] = {}

class WorkersModel(WorkersEditModel):
    """Worker display model."""
    id: str = ""
    ip: str = ""
    last_connection: str = ""
    pools: list[str] = []
    tags: list[str] = []
