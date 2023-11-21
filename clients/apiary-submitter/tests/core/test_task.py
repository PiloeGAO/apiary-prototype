"""Testing the :class:`apiary_submitter.core.task.Task`"""
from apiary_submitter.core.task import Task


def test_default():
    """Test a default task setup with only rhe command provided."""
    task = Task("echo 1")

    assert task.name == "echo 1"
    assert task.command == "echo 1"
    assert task.status == 0
    assert task.tags == []
    assert task.metadata == {}
    assert not task.childrens


def test_childrens():
    """Test children functions."""
    parent = Task("echo 1")

    assert not parent.childrens
    assert not parent.has_childrens

    child = Task("echo 2")
    parent.add_child(child)

    assert parent.childrens == [child]
    assert parent.has_childrens
    assert parent > child
    assert child < parent
