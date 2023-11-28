"""List of all the status definitions."""
from enum import IntEnum, auto, unique


class MetaStatuses(IntEnum):
    """Enum metaclass."""

    @classmethod
    def to_dict(cls):
        """Override the dict proterty to return the correct dictionnary.

        Returns:
            dict: Enum elements.
        """
        return {i.name: i.value for i in cls}


@unique
class JobStatuses(MetaStatuses):
    """Statuses for jobs."""

    WAITING = auto()
    IN_PROGRESS = auto()
    DONE = auto()
    ERROR = auto()
    PAUSED = auto()


@unique
class TaskStatuses(MetaStatuses):
    """Statuses for tasks."""

    READY = auto()
    IN_PROGRESS = auto()
    DONE = auto()
    ERROR = auto()
    PAUSED = auto()


@unique
class RunStatuses(MetaStatuses):
    """Statuses for runs."""

    IN_PROGRESS = auto()
    DONE = auto()
    ERROR = auto()
