# apiary-prototype
This is a prototype for the Apiary Render Farm system.

## Project Structure

### Build Scripts (./build_scripts)

A set of utility scripts used for building.

### Clients (./clients)

The official supported clients.

#### Apiary OpenAPI (Auto-generated)

An auto-generated python module used to communicate with the API directly. This is not pushed to the repository, must be builded locally from the current online API and never be edited by hand.

Process used to generate it:
```shell
# Set the API host address. The default value `http://127.0.0.1` will be used if not set.
> export APIARY_HOST="http://your.host.local"
# At the root of the repository.
> python ./build_scripts/generate_apiary_openapi.py
```

#### Apiary Submitter

This is a python module used to send jobs to the farm. Please see the official documentation for more information: *link to be added*

Example of usage:
```python
from apiary_submitter.core.job import Job
from apiary_submitter.core.task import Task
from apiary_submitter.core.submitter import Submitter
from apiary_submitter.exceptions import SubmitException

# Create a list of tasks and chain them.
parent_task = Task("echo 1")
child_task = Task("echo 2")
parent_task.add_child(child_task)

# Create a job with the parent task, the child tasks will automatically be loaded.
demo_job = Job(
    name="Submitter Tester",
    priority=750,
    tasks=[parent_task],
    pools=["demo"],
    tags=["tests"],
    metadata={"hello":"world"}
)

# Create a submitter instance.
submitter = Submitter(host=os.environ.get("API_HOST", "http://localhost"))

# Send the job to the API.
job_id = None
try:
    job_id = submitter.submit(job)
except SubmitException as error:
    print(f"Job submission failed: {error}")

print(f"Job ID: {job_id}")
```

### Core (./core)

The core components for the service. A docker compose file is provided for development.

#### Apiary API

The main entry point for the API.

#### Apiary Jobs

A private API used to manage and store jobs, tasks and runs.
