import datetime
import json
import os
import logging

import pymysql
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from opencensus.ext.azure.log_exporter import AzureLogHandler

from task_management import TaskRepository, TaskFactory

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)
log = logging.getLogger(__name__)
load_dotenv(override=True)

app_insights_key = os.getenv("APPLICATIONINSIGHTS_KEY")

if not app_insights_key:
    raise ValueError("APPLICATIONINSIGHTS_KEY environment variable not set!")

log.addHandler(AzureLogHandler(
    connection_string=f"InstrumentationKey={app_insights_key}"))

db_host = os.getenv("DB_HOST")

if not db_host:
    raise ValueError("DB_HOST environment variable not set!")

db_user = os.getenv("DB_USER")

if not db_user:
    raise ValueError("DB_USER environment variable not set!")

db_user_password = os.getenv("DB_USER_PASSWORD")

if not db_user_password:
    raise ValueError("DB_USER_PASSWORD environment variable not set!")

db = pymysql.connect(host=db_host, user=db_user, password=db_user_password, db="tasks")

create_table_sql = """CREATE TABLE tasks (
    id varchar(255) NOT NULL,
    description varchar(512) NOT NULL,
    owner varchar(255) NOT NULL,
	due_date datetime NULL,
	complete_date datetime NULL,
	complete bit NOT NULL
    PRIMARY KEY (`id`)
)"""

with db.cursor() as cursor:
    cursor.execute(create_table_sql)
    db.commit()
    log.info("Created tasks table.")

app = Flask(__name__)
repo = TaskRepository(db)


@app.route("/ping")
def ping():
    return json.dumps({"meta": {"desc": "Task API", "ver": "1.0"}})


@app.route("/tasks", methods=["POST"])
def add_task():
    task = TaskFactory.create(json.loads(request.data))
    new_task = repo.add_task(task)
    return jsonify(new_task), 201


@app.route("/tasks/<owner>", methods=["GET"])
def get_tasks(owner):
    if "include_closed" in request.args:
        tasks = repo.get_tasks(owner, True)
    else:
        tasks = repo.get_tasks(owner)

    return jsonify([task for task in tasks])


@app.route("/tasks/<owner>/<task_id>/complete", methods=["PUT"])
def complete_task(owner, task_id):
    complete_date = datetime.datetime.now()
    request_obj = json.loads(request.data)

    if "complete_date" in request_obj:
        complete_date = request_obj["complete_date"]

    repo.complete_task(task_id, owner, complete_date)
    return jsonify({}), 204


port_str = os.getenv("FLASK_RUN_PORT", "5000")
app.run(port=int(port_str), host="0.0.0.0")
