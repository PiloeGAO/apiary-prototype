"""Model definition for the status request."""
from pydantic import BaseModel

class StatusModel(BaseModel):
    """Status base model."""
    name: str
    description: str
    version: str