"""Job class description."""
from apiary_submitter.core.task import Task
from apiary_submitter.constants import MIN_PRIORITY, MAX_PRIORITY


class Job:
    """Job class."""

    def __init__(
        self, name, pools=None, priority=500, tasks=None, tags=None, metadata=None
    ) -> None:
        """Class initializer.

        Args:
            name (str): Name of the job to be spooled on the farm.
            pools (list[str], optional): List of pools name. Defaults to None.
            priority (int, optional): Job priority. Defaults to 500.
            tasks (list[:class:`apiary_submitter.core.Task`], optional): Tasks of the job.
                Defaults to None.
            tags (list[str]): List of tags. Defaults to None.
            metadata (dict, optional): Job metadatas. Defaults to None.
        """
        self.name = name
        self.pools = []
        self.priority = priority if MIN_PRIORITY <= priority <= MAX_PRIORITY else 500
        self.tasks = []
        self.tags = []
        self.metadata = metadata if isinstance(metadata, dict) else {}

        if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
            raise ValueError(
                f"Piority must be in the range {MIN_PRIORITY} - {MAX_PRIORITY}."
            )

        if isinstance(pools, list):
            self.pools = [pool for pool in pools if isinstance(pool, str)]

        if isinstance(tasks, list):
            self.tasks = [task for task in tasks if isinstance(task, Task)]

        if isinstance(tags, list):
            self.tags = [tag for tag in tags if isinstance(tag, str)]

    @property
    def all_tasks(self) -> list[Task]:
        """list[:class:`apiary_submitter.core.Task`]: List of tasks and tasks childrens.

        We are simulating a dependency graph by ordering the tasks childrens before returning.
        """

        def iter_childrens(task: Task) -> list[Task]:
            """Recursive function to get the childrens of the task.

            Args:
                task (:class:`apiary_submitter.core.Task`): Task to extract childrens.

            Returns:
                list[:class:`apiary_submitter.core.Task`]: Task with childrens.
            """
            tasks_list = []
            for task_child in task.childrens:
                tasks_list.append(task_child)
                tasks_list.extend(iter_childrens(task_child))
            return tasks_list

        def remove_duplicates(tasks: list[Task]) -> list[Task]:
            """Remove the ducplicates from a list of Task.

            Args:
                tasks (list[:class:`apiary_submitter.core.Task`]):
                    List to clear. Defaults to list[:class:`apiary_submitter.core.Task`].

            Returns:
                list[:class:`apiary_submitter.core.Task`]: Optimized list.
            """
            tasks.reverse()
            tasks = list(dict.fromkeys(tasks))
            tasks.reverse()
            return tasks

        all_tasks_list = self.tasks.copy()
        all_tasks_list.sort()
        for task in self.tasks:
            task_index = all_tasks_list.index(task)
            for sub_task in iter_childrens(task):
                task_index += 1
                all_tasks_list.insert(task_index, sub_task)

        return remove_duplicates(all_tasks_list)
