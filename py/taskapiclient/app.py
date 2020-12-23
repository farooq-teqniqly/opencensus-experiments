import logging
import os
from datetime import datetime
from datetime import timedelta
from uuid import uuid4

import requests
from dotenv import load_dotenv


def main():
    logger = logging.getLogger(__name__)
    load_dotenv(override=True)

    task_api_base_url = os.getenv("TASK_API_BASE_URL")

    if not task_api_base_url:
        raise ValueError("TASK_API_BASE_URL environment variable not set!")

    task_run_interval = 10
    task_run_interval_str = os.getenv("RUN_INTERVAL")

    if task_run_interval_str:
        task_run_interval = int(task_run_interval_str)

    stop_after = 60
    stop_after_str = os.getenv("STOP_AFTER")

    if stop_after_str:
        stop_after = int(stop_after_str)

    task_owner = os.getenv("TASK_OWNER")

    if not task_owner:
        task_owner = "default-user"

    start_time = datetime.now()

    while datetime.now() - start_time < timedelta(seconds=stop_after):
        logger.info("Adding task...")

        response = requests.post(
            f"{task_api_base_url}/tasks/{task_owner}",
            {
                "task_id": str(uuid4()),
                "due_date": datetime.now() + timedelta(days=1),
                "description": "Buy birthday gift.",
                "owner": task_owner
            })

        if response.status_code >= 400:
            raise Exception({
                "status_code": response.status_code,
                "reason": response.reason
            })

        logger.info(f"Task added.\n{response.json()}")

    logger.info(f"All tasks for {task_owner}:")
    response = requests.get(f"{task_api_base_url}/tasks/{task_owner}")

    if response.status_code >= 400:
        raise Exception({
            "status_code": response.status_code,
            "reason": response.reason
        })

    logger.info(response.json())


if __name__ == "__main__":
    main()
