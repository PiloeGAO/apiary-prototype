"""Model definition for the API status request."""
from pydantic import BaseModel


class APIStatusModel(BaseModel):
    """Status base model."""

    name: str
    description: str
    version: str
