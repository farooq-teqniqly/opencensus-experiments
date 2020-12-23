import datetime
import json
import os
import logging

from dotenv import load_dotenv
from flask import Flask, request, jsonify

from task_management import TaskRepository, TaskFactory

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
load_dotenv(override=True)
app = Flask(__name__)
repo = TaskRepository()


@app.route("/ping")
def ping():
    return json.dumps({'meta': {
        "desc": "Task API",
        "ver": "1.0"
    }})


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
