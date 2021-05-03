# The path to a task is list_id, taskseries_id, task_id
# List object has a list_id and a name
# Does each property change cause a method call? If that happens, can't enforce start/end date ordering
# If we have a commit method on tasks, it will need to track what has changed
# When you fill in the task object, does it always have all the field information? yes
# Tasks have start/due date/time. starts have to be set before due when trying to simulate atomicity
# How to represent task series?
# Some task properties are really properties of the task list (e.g. tags, notes). I suppose this means that if you change the tags on a repeating task, the next one will have it's tags changed too
# When you set a task property, it looks like you get the full task response back

from datetime import datetime
from typing import Literal, Union

from pydantic import BaseModel

from .utils import EmptyStrToNone

class Task(BaseModel):
	added: datetime
	completed: Union[EmptyStrToNone[datetime]]
	deleted: Union[EmptyStrToNone[datetime]]
	due: Union[EmptyStrToNone[datetime]]
	estimate: str
	has_due_time: bool
	has_start_time: bool
	id: str
	postponed: int
	priority: Literal['N', '1', '2', '3']
	start: Union[EmptyStrToNone[datetime]]
