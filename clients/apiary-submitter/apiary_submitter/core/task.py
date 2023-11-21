"""Task class description."""


class Task:
    """Task class."""

    def __init__(
        self, command: str, name="", status=None, tags=None, metadata=None
    ) -> None:
        """Class initializer.

        Args:
            command (str): Command of the task.
            name (str, optional): Name of the task. Defaults to "".
            status (int, optional): Task status. Defaults to None.
            tags (list[str], optional): List of tags. Defaults to None.
            metadata (dict, optional): Task metadatas. Defaults to None.
        """
        self.name = name if name else command
        self.command = command
        self.status = status if status else 0
        self.tags = []
        self.metadata = metadata if isinstance(metadata, dict) else {}
        self.childrens = []

        if isinstance(tags, list):
            self.tags = [tag for tag in tags if isinstance(tag, str)]

    def __lt__(self, other) -> bool:
        """Sorting function for tasks.

        Args:
            other (ass:`apiary_submitter.core.Task`): Other task.

        Returns:
            bool: `True` if `self` is less than `other`, `False` otherwise.
        """
        return self.childrens < other.childrens

    def add_child(self, task) -> None:
        """Add a children task to the task.

        Args:
            task (:class:`apiary_submitter.core.Task`): Children task.

        Raises:
            ValueError: Children task must be of type :class:`apiary_submitter.core.Task`.
        """
        if not isinstance(task, type(self)):
            raise ValueError("Task children must be a task.")

        self.childrens.append(task)

    @property
    def has_childrens(self) -> bool:
        """bool: `True` if the Task have one or more childrens, `False` otherwise."""
        return True if len(self.childrens) > 0 else False
