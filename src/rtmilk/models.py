from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Field, constr, validator # pylint: disable=no-name-in-module
from pydantic.types import ConstrainedStr # pylint: disable=no-name-in-module

from .utils import EmptyStrToNone

class RTMError(Exception):
	def __init__(self, code, message):
		super().__init__(self)
		self.code = code
		self.message = message

	def __repr__(self):
		return f'<RTMError code={self.code}, message={self.message}>'

class ErrorData(BaseModel):
	code: int
	msg: str

class OkStat(BaseModel):
	stat: constr(regex='ok')

class FailStat(BaseModel):
	stat: constr(regex='fail')
	err: ErrorData

class EchoResponse(OkStat):
	__test__ = False # avoid pytest warning
	method: constr(regex='rtm.test.echo')

class RTMList(BaseModel):
	id: int
	name: str
	deleted: bool
	locked: bool
	archived: bool
	position: int
	smart: bool

	@classmethod
	@validator('smart')
	def NotASmartList(cls, value: bool) -> bool:
		if value is not False:
			raise ValueError('Must be False for non-smart lists')
		return value

class RTMSmartList(RTMList):
	filter: str

	@classmethod
	@validator('smart')
	def IsASmartList(cls, value: bool) -> bool:
		if value is not True:
			raise ValueError('Must be True for smart lists')
		return value

class ListPayload(BaseModel):
	list: list[Union[RTMSmartList, RTMList]]

class SingleListResponse(OkStat):
	list: Union[RTMSmartList, RTMList]

class ListsResponse(OkStat):
	lists: ListPayload

class PermsEnum(str, Enum):
	read = 'read'
	write = 'write'
	delete = 'delete'

class User(BaseModel):
	id: str
	username: str
	fullname: str

class AuthResponsePayload(BaseModel):
	perms: PermsEnum
	token: str
	user: User

class AuthResponse(OkStat):
	auth: AuthResponsePayload

class TimelineResponse(OkStat):
	timeline: str # using str rather than int because you can't do any arithmetic with it

class PriorityEnum(Enum):
	NoPriority = 'N'
	Priority1 = '1'
	Priority2 = '2'
	Priority3 = '3'

class PriorityDirectionEnum(Enum):
	Up = 'up'
	Down = 'down'

class Task(BaseModel):
	id: str
	added: datetime
	completed: Optional[EmptyStrToNone[datetime]]
	deleted: Optional[EmptyStrToNone[datetime]]
	due: Optional[EmptyStrToNone[datetime]]
	estimate: str
	has_due_time: bool
	has_start_time: bool
	postponed: int
	priority: PriorityEnum
	start: Optional[EmptyStrToNone[datetime]]

class NotesResponsePayload(BaseModel):
	id: str
	created: datetime
	modified: datetime
	title: str
	body: str = Field(None, alias='$t')

class Transaction(BaseModel):
	id: str
	undoable: bool

class NotesResponse(OkStat):
	transaction: Transaction
	note: NotesResponsePayload

class NotePayload(BaseModel):
	note: list[NotesResponsePayload]

class Tags(BaseModel):
	tag: list[str]

class TaskSeries(BaseModel):
	id: str
	created: datetime
	modified: datetime
	name: str
	source: str
	url: EmptyStrToNone[AnyHttpUrl]
	location_id: str
	participants: list[str]
	notes: Union[list[str], NotePayload]
	task: list[Task]
	# in the case where it's a list, it seems to be always an empty list
	tags: Union[Tags, list[str]]

class TaskPayload(BaseModel):
	id: str
	taskseries: list[TaskSeries]

class TaskResponse(OkStat):
	transaction: Transaction
	list: TaskPayload

class TasksInListPayload(BaseModel):
	id: str
	# can be missing if there are no tasks in the list
	taskseries: Optional[list[TaskSeries]]

class TaskListPayload(BaseModel):
	rev: str
	# if there are are no tasks in the list, this node is missing
	list: Optional[list[TasksInListPayload]]

class TaskListResponse(OkStat):
	tasks: TaskListPayload

class TagObject(BaseModel):
	name: str

class TagForList(BaseModel):
	tag: list[TagObject]

class TagListResponse(OkStat):
	tags: TagForList

class DateFormatEnum(IntEnum):
	European = 0
	American = 1

class TimeFormatEnum(IntEnum):
	Format12Hour = 0
	Format24Hour = 1

class SettingsPayload(BaseModel):
	timezone: str
	dateformat: DateFormatEnum # 0 for Euro format, 1 for US format
	timeformat: TimeFormatEnum # 0 for 12-hour format, 1 for 24-hour format
	defaultlist: str
	language: str
	defaultduedate: str
	pro: bool

class SettingsResponse(OkStat):
	settings: SettingsPayload

class Topic(BaseModel):
	topic: list[str]

class TopicListResponse(OkStat):
	topics: Topic

class SubscriptionData:
	id: str
	url: str
	format: ConstrainedStr('json')
	expires: datetime
	pending: bool
	topics: list[str]

class SubscriptionPayload(BaseModel, SubscriptionData):
	pass

class SubscriptionResponse(OkStat, SubscriptionData):
	transaction: Transaction
	subscription: SubscriptionPayload

class SubscriptionListResponse(OkStat):
	subscriptions: list[SubscriptionPayload]
