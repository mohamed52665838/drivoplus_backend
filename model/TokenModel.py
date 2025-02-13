from flask_pydantic_spec.types import ResponseBase
from pydantic import BaseModel


class TokenModel(ResponseBase):
    access_token: str
    refresh_token: str