from __future__ import annotations

from datetime import datetime
from enum import Enum, IntEnum

from pydantic import BaseModel, Field, constr, field_validator

from ._utils import EmptyStrToNone

class RTMError(Exception):
	def __init__(self, code, message):
		super().__init__(self)
		self.code = code
		self.message = message

	def __repr__(self):
		return f'RTMError({self.code=}, {self.message=})'

class ErrorData(BaseModel):
	code: int
	msg: str

class OkStat(BaseModel):
	stat: constr(pattern='ok')

class FailStat(BaseModel):
	stat: constr(pattern='fail')
	err: ErrorData

class EchoResponse(OkStat):
	__test__ = False # avoid pytest warning
	method: constr(pattern='rtm.test.echo')

class RTMList(BaseModel):
	id: str
	name: str
	deleted: bool
	locked: bool
	archived: bool
	position: int
	smart: bool

	@classmethod
	@field_validator('smart')
	@classmethod
	def NotASmartList(cls, value: bool) -> bool:
		if value is not False:
			raise ValueError('Must be False for non-smart lists')
		return value

class RTMSmartList(RTMList):
	filter: str

	@classmethod
	@field_validator('smart')
	@classmethod
	def IsASmartList(cls, value: bool) -> bool:
		if value is not True:
			raise ValueError('Must be True for smart lists')
		return value

class ListPayload(BaseModel):
	list: list[RTMSmartList | RTMList]

class SingleListResponse(OkStat):
	list: RTMSmartList | RTMList

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
	completed: EmptyStrToNone[datetime | None]
	deleted: EmptyStrToNone[datetime | None]
	due: EmptyStrToNone[datetime | None]
	estimate: str
	has_due_time: bool
	has_start_time: bool
	postponed: int
	priority: PriorityEnum
	start: EmptyStrToNone[datetime | None]

class Note(BaseModel):
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
	note: Note

class NotePayload(BaseModel):
	note: list[Note]

class Tags(BaseModel):
	tag: list[str]

class TaskSeries(BaseModel):
	id: str
	created: datetime
	modified: datetime
	name: str
	source: str
	url: EmptyStrToNone[str | None]
	location_id: str
	participants: list[str]

	# see test_that_unions_are_necessary_for_notes_list for why the Union is necessary
	# in the case where this is a list[str], it's always an empty list
	notes: NotePayload | list[str]
	task: list[Task]

	# see test_that_unions_are_necessary_for_tag_list for why the Union is necessary
	# in the case where this is a list[str], it's always an empty list
	tags: Tags | list[str]

class TaskPayload(BaseModel):
	id: str
	taskseries: list[TaskSeries]

class TaskResponse(OkStat):
	transaction: Transaction
	list: TaskPayload

class TasksInListPayload(BaseModel):
	id: str
	# can be missing if there are no tasks in the list returned from TasksGetList with just a listid
	taskseries: list[TaskSeries] | None = None

# hack to make the module import
ListOfTasksInListPayload = list[TasksInListPayload]

class TaskListPayload(BaseModel):
	rev: str
	# if there are are no tasks in the list, returned from TasksGetList via a filter, this node is missing
	list: ListOfTasksInListPayload | None = None

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

class SubscriptionPayload(BaseModel):
	id: str
	url: str
	format: constr(pattern='json')
	expires: datetime
	pending: bool
	topics: Topic | list[str]

# SubscriptionPayload.model_rebuild()

class SubscriptionResponse(OkStat):
	transaction: Transaction
	subscription: SubscriptionPayload

class SubscriptionList(BaseModel):
	subscription: list[SubscriptionPayload]

class SubscriptionListResponse(OkStat):
	subscriptions: SubscriptionList | list[SubscriptionPayload]
