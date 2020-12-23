import json
import logging
import os
from datetime import datetime
from datetime import timedelta
from uuid import uuid4
from time import sleep

import requests
from dotenv import load_dotenv


def main():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(__name__)
    load_dotenv(override=True)

    task_api_base_url = os.getenv("TASK_API_BASE_URL")

    if not task_api_base_url:
        raise ValueError("TASK_API_BASE_URL environment variable not set!")

    task_run_interval_str = os.getenv("RUN_INTERVAL", "10")
    stop_after_str = os.getenv("STOP_AFTER", "60")
    task_owner = os.getenv("TASK_OWNER", "default-user")

    start_time = datetime.now()

    while datetime.now() - start_time < timedelta(seconds=int(stop_after_str)):
        logger.info("Adding task...")

        task = {
            "task_id": str(uuid4()),
            "due_date": str(datetime.now() + timedelta(days=1)),
            "description": "Buy birthday gift.",
            "owner": task_owner
        }

        response = requests.post(
            f"{task_api_base_url}/tasks",
            json.dumps(task))

        if response.status_code >= 400:
            raise Exception({
                "status_code": response.status_code,
                "reason": response.reason
            })

        logger.info(f"Task added.\n{response.json()}")
        sleep(int(task_run_interval_str))

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
