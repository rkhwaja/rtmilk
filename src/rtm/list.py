from typing import Optional

from pydantic import BaseModel

class List(BaseModel):
	id: str
	name: str
	deleted: bool
	locked: bool
	archived: bool
	position: int
	smart: bool
	filter: Optional[str]
