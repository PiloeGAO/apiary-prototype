"""List of all the constants used in the jobs microservices."""
import os

DB_HOST = os.getenv("DB_HOST") or "127.0.0.1"
DB_PORT = os.getenv("DB_PORT") or 27017
DB_USER = os.getenv("DB_USER") or "dbroot"
DB_PASSWORD = os.getenv("DB_PASSWORD") or "dbpass"
