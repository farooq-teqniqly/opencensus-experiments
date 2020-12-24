import json
import logging
import os
from datetime import datetime
from datetime import timedelta
from uuid import uuid4
from time import sleep

import requests
from dotenv import load_dotenv
from opencensus.ext.azure.log_exporter import AzureLogHandler
from exceptions import HttpException


def main(logger):
    app_insights_key = os.getenv("APPLICATIONINSIGHTS_KEY")

    if app_insights_key:
        logger.addHandler(AzureLogHandler(
            connection_string=f"InstrumentationKey={app_insights_key}"))

        logger.info("Application Insights logging enabled.")

    task_api_base_url = os.getenv("TASK_API_BASE_URL")

    if not task_api_base_url:
        raise ValueError("TASK_API_BASE_URL environment variable not set!")

    task_run_interval_str = os.getenv("RUN_INTERVAL", "10")
    stop_after_str = os.getenv("STOP_AFTER", "60")
    task_owner = os.getenv("TASK_OWNER", "default-user")

    logger.info("Acquiring token.")

    auth_api_base_url = os.getenv("AUTH_API_BASE_URL")

    if not auth_api_base_url:
        raise ValueError("AUTH_API_BASE_URL environment variable not set!")

    client_id = os.getenv("CLIENT_ID")

    if not client_id:
        raise ValueError("CLIENT_ID environment variable not set!")

    secret = os.getenv("SECRET")

    if not secret:
        raise ValueError("SECRET environment variable not set!")

    token_request = {
        "client_id": client_id,
        "secret": secret
    }

    response = requests.post(
        f"{auth_api_base_url}/token",
        json.dumps(token_request))

    if response.status_code >= 400:
        props = {
            "custom_dimensions": {
                "status_code": response.status_code,
                "reason": response.reason
            }
        }

        raise HttpException("Could not get token.", props)

    logger.info("Token acquired.")

    token_response = json.loads(response.text)

    task_api_request_header = {
        "Authorization": token_response["value"]
    }

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
            json.dumps(task),
            headers=task_api_request_header)

        if response.status_code >= 400:
            props = {
                "custom_dimensions": {
                    "status_code": response.status_code,
                    "reason": response.reason
                }
            }

            raise HttpException("Could not add task.", props)

        logger.debug(f"Task added.")
        sleep(int(task_run_interval_str))

    logger.info(f"All tasks for {task_owner}:")
    response = requests.get(
        f"{task_api_base_url}/tasks/{task_owner}",
        headers=task_api_request_header)

    if response.status_code >= 400:
        props = {
            "custom_dimensions": {
                "status_code": response.status_code,
                "reason": response.reason
            }
        }

        raise HttpException(f"Could not get tasks for {task_owner}.", props)

    props = {
        "custom_dimensions": {
            "tasks": str(response.json())
        }
    }

    logger.debug(f"All tasks for {task_owner}.", extra=props)


if __name__ == "__main__":
    load_dotenv(override=True)
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(level=log_level)
    log = logging.getLogger(__name__)

    try:
        main(log)
    except HttpException as ex:
        log.exception(ex, extra=ex.props)
