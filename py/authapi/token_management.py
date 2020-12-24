import base64
import logging
import os

from dataclasses import dataclass

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)

@dataclass
class TokenRequest:
    client_id: str
    secret: str


class TokenRequestFactory:
    @classmethod
    def create_token_request(cls, request_data) -> TokenRequest:
        if "client_id" not in request_data:
            raise ValueError("Provide a client id.")

        if "secret" not in request_data:
            raise ValueError("Provide a secret.")

        return TokenRequest(request_data["client_id"], request_data["secret"])


@dataclass
class Token:
    value: str


class TokenFactory:
    @classmethod
    def create_token(cls, token_request: TokenRequest) -> Token:
        if "badapp" in token_request.client_id:
            raise ValueError("Application not allowed!")

        data = f"{token_request.client_id};{token_request.secret}"
        encoded_bytes = base64.b64encode(data.encode("utf-8"))
        return Token(str(encoded_bytes, "utf-8"))
