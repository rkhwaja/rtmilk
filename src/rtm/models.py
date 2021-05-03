from typing import Dict

from pydantic import BaseModel

class Response:
	stat: str

class EchoResponse(BaseModel):
	method: str
	params: Dict
