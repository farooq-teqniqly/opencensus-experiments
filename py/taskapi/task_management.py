import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Generator, Union


@dataclass
class Task:
    id: str
    description: str
    owner: str
    due_date: Union[datetime, None]
    complete: bool
    complete_date: Union[datetime, None]


class TaskFactory:
    @classmethod
    def create(cls, request_data) -> Task:
        task_id = str(uuid.uuid4())
        due_date = None
        complete = False
        complete_date = None

        if "description" not in request_data:
            raise ValueError("Provide a description.")

        description = request_data["description"]

        if "owner" not in request_data:
            raise ValueError("Provide an owner.")

        owner = request_data["owner"]

        if "due_date" in request_data:
            due_date = request_data["due_date"]

        if "complete" in request_data:
            complete = request_data["complete"]

        if "complete_date" in request_data:
            complete_date = request_data["complete_date"]

        return Task(
            task_id,
            description,
            owner,
            due_date,
            complete,
            complete_date)


class TaskRepository:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def add_task(self, task: Task):
        task.id = str(uuid.uuid4())
        self.tasks.update({task.id: task})
        return task

    def get_tasks(self, owner: uuid, include_closed_tasks=False) \
            -> Generator[Task, None, None]:
        if include_closed_tasks:
            return (task for task in self.tasks.values() if task.owner == owner)

        return (task for task in self.tasks.values() if
                task.owner == owner and task.complete is False)

    def complete_task(self, task_id: str, owner: str, complete_date: datetime):
        task = self.tasks[task_id]

        if task.owner != owner:
            return

        task.complete = True
        task.complete_date = complete_date
