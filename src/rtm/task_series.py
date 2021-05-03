from datetime import datetime
from typing import List

from pydantic import BaseModel, AnyHttpUrl

from .tasks import Task
from .utils import EmptyStrToNone

class TaskSeries(BaseModel):
	id: str
	created: datetime
	modified: datetime
	name: str
	source: str
	url: EmptyStrToNone[AnyHttpUrl]
	location_id: str
	tags: List[str]
	participants: List[str]
	notes: List[str]
	task: List[Task]
