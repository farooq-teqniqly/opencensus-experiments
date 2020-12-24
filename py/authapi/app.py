import json
import logging
import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response

from token_management import TokenRequestFactory, TokenFactory

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
load_dotenv(override=True)
app = Flask(__name__)


@app.route("/token", methods=["POST"])
def get_token():
    token_request = TokenRequestFactory.create_token_request(json.loads(request.data))

    try:
        token = TokenFactory.create_token(token_request)
    except ValueError:
        return Response(status=401)

    return jsonify(token)


port_str = os.getenv("FLASK_RUN_PORT", "5000")
app.run(port=int(port_str), host="0.0.0.0")
