"""List of all the constants used in the API."""
import os

DEBUG = os.environ.get("DEBUG", False)

JOBS_HOSTNAME = os.getenv("JOBS_HOSTNAME")
WORKERS_HOSTNAME = os.getenv("WORKERS_HOSTNAME")
