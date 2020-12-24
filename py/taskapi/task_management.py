import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Generator, Union

from pymysql import Connection


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
    def __init__(self, db: Connection):
        self.db = db

    def add_task(self, task: Task):
        task.id = str(uuid.uuid4())

        with self.db.cursor() as cursor:
            sql = "INSERT INTO tasks VALUES (%s, %s, %s, '%s', '%s', )"

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
