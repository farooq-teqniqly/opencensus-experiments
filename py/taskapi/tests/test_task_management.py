import datetime
import uuid

from task_management import TaskRepository, Task


def test_add_task():
    repo = TaskRepository()
    task_id = str(uuid.uuid4())
    owner = str(uuid.uuid4())
    task = Task(task_id, "new task", owner, None, False, None)
    repo.add_task(task)
    tasks = [repo.get_tasks(owner)]
    assert len(tasks) == 1


def test_get_tasks_returns_open_tasks_by_default():
    repo = TaskRepository()
    task_id = str(uuid.uuid4())
    owner = str(uuid.uuid4())
    task = Task(task_id, "new task", owner, None, True, None)
    repo.add_task(task)
    tasks = [task for task in repo.get_tasks(owner)]
    assert len(tasks) == 0


def test_complete_task():
    repo = TaskRepository()
    task_id = str(uuid.uuid4())
    owner = str(uuid.uuid4())
    task = Task(task_id, "new task", owner, None, False, None)
    repo.add_task(task)
    task = [task for task in repo.get_tasks(owner, True) if task.owner == owner][0]
    assert task.complete is False

    complete_date = datetime.datetime.now()
    repo.complete_task(task.id, owner, complete_date=complete_date)

    assert task.complete is True
    assert task.complete_date == complete_date
