"""Testing the :class:`apiary_submitter.core.job.Job`"""
import pytest

from apiary_submitter.core.job import Job
from apiary_submitter.core.task import Task
from apiary_submitter.constants import MIN_PRIORITY, MAX_PRIORITY


def test_default():
    """Test a default job setup with only the name provided."""
    job = Job(name="Job 01")

    assert job.name == "Job 01"
    assert job.pools == []
    assert job.priority == 500
    assert job.tasks == []
    assert job.tags == []
    assert job.metadata == {}


def test_pools():
    """Test pools."""
    job = Job(name="Job 01", pools=[1, 2, 3, True, False])
    assert job.pools == []

    job = Job(name="Job 02", pools=[1, "two", 3, True, False])
    assert job.pools == ["two"]


def test_priority():
    """Test priority."""
    job = Job(name="Job 01", priority=750)
    assert job.priority == 750

    with pytest.raises(
        ValueError,
        match=f"Piority must be in the range {MIN_PRIORITY} - {MAX_PRIORITY}.",
    ):
        job = Job(name="Job 02", priority=-1)

    with pytest.raises(
        ValueError,
        match=f"Piority must be in the range {MIN_PRIORITY} - {MAX_PRIORITY}.",
    ):
        job = Job(name="Job 02", priority=1001)


def test_tasks():
    """Test tasks."""
    job = Job(name="Job 01", tasks=[1, 2, 3, True, False])
    assert job.tasks == []

    task = Task("echo 1")
    job = Job(name="Job 02", tasks=[1, task, 3, True, False])
    assert job.tasks == [task]


def test_tags():
    """Test tags."""
    job = Job(name="Job 01", tags=["tag01", 1, True])
    assert job.tags == ["tag01"]


def test_all_tasks():
    """Test the all_tasks property."""
    parent_task = Task("echo 1")
    inter_task = Task("echo 2")
    parent_task.add_child(inter_task)
    child_task = Task("echo 3")
    inter_task.add_child(child_task)

    job = Job(name="Job 01", tasks=[parent_task])
    assert job.tasks == [parent_task]
    assert job.all_tasks == [parent_task, inter_task, child_task]

    parent_task = Task("echo 1")
    inter_task = Task("echo 2")
    parent_task.add_child(inter_task)
    child_task = Task("echo 3")
    parent_task.add_child(child_task)
    inter_task.add_child(child_task)

    job = Job(name="Job 02", tasks=[parent_task])
    assert job.tasks == [parent_task]
    assert job.all_tasks == [parent_task, inter_task, child_task]

    parent_task = Task("echo 1")
    child_task = Task("echo 2")
    parent_task.add_child(child_task)
    another_task = Task("echo 3")

    job = Job(name="Job 03", tasks=[parent_task, another_task])
    assert job.tasks == [parent_task, another_task]
    assert job.all_tasks == [another_task, parent_task, child_task]

    job = Job(name="Job 04", tasks=[another_task, parent_task])
    assert job.tasks == [another_task, parent_task]
    assert job.all_tasks == [another_task, parent_task, child_task]
