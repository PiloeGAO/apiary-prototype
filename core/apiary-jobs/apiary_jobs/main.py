"""Apiary Jobs package file."""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    """Demo endpoint.

    Returns:
        dict: Hello world dict.
    """
    return {"Hello": "Jobs"}

@app.get("/status")
async def get_status():
    """Get the status of the microservice.

    Returns:
        dict: Microservice datas.
    """
    return {
        "name": "ApiaryJobs microservice",
        "version": "0.0.1",
    }
