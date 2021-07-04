from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional, Union

from pydantic import AnyHttpUrl, BaseModel, Field, constr, validator # pylint: disable=no-name-in-module

from .utils import EmptyStrToNone

class RTMError2(BaseModel):
	code: int
	msg: str

class OkStat(BaseModel):
	stat: constr(regex='ok')

class FailStat(BaseModel):
	stat: constr(regex='fail')
	err: RTMError2

class TestEchoResponse(OkStat):
	__test__ = False # avoid pytest warning
	method: constr(regex='rtm.test.echo')

class RTMGenericListId(BaseModel):
	id: int

class RTMGenericList(RTMGenericListId):
	name: str
	deleted: bool
	locked: bool
	archived: bool
	position: int

class RTMList(RTMGenericList):
	smart: bool # TODO - split on whether this is true or false

	@classmethod
	@validator('smart')
	def NotASmartList(cls, value: bool) -> bool:
		if value is not False:
			raise ValueError('must be False for non-smart lists')
		return value

class RTMSmartList(RTMList):
	smart: bool
	filter: str

	@classmethod
	@validator('smart')
	def IsASmartList(cls, value: bool) -> bool:
		if value is not True:
			raise ValueError('must be True for non-smart lists')
		return value

class List(BaseModel):
	list: list[Union[RTMSmartList, RTMList]]

class ListsGetListResponse(OkStat):
	lists: List

class PermsEnum(str, Enum):
	read = 'read'
	write = 'write'
	delete = 'delete'

class User(BaseModel):
	id: str
	username: str
	fullname: str

class AuthCheckTokenResponsePayload(BaseModel):
	perms: PermsEnum
	token: str
	user: User

class AuthCheckTokenResponse(OkStat):
	auth: AuthCheckTokenResponsePayload

class TimelinesCreateResponse(OkStat):
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
	completed: Union[EmptyStrToNone[datetime]]
	deleted: Union[EmptyStrToNone[datetime]]
	due: Union[EmptyStrToNone[datetime]]
	estimate: str
	has_due_time: bool
	has_start_time: bool
	postponed: int
	priority: PriorityEnum
	start: Union[EmptyStrToNone[datetime]]

# <note id="169624" created="2015-05-07T11:26:49Z" modified="2015-05-07T11:26:49Z" title="Note Title">Note Body</note>
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

class NotesResponse2(BaseModel):
	note: list[NotesResponsePayload]

class TaskSeriesBase(BaseModel):
	id: str
	created: datetime
	modified: datetime
	name: str
	source: str
	url: EmptyStrToNone[AnyHttpUrl]
	location_id: str
	participants: list[str]
	notes: Union[list[str], NotesResponse2]
	task: list[Task]

class TaskSeries(TaskSeriesBase):
	tags: list[str]

class Tag(BaseModel):
	tag: list[str]

class TaskSeriesForTags(TaskSeriesBase):
	tags: Union[Tag, list[str]]

class TasksResponsePayload(BaseModel):
	id: str
	taskseries: list[TaskSeries]

class TasksTagsResponsePayload(BaseModel):
	id: str
	taskseries: list[TaskSeriesForTags]

class TasksResponse(OkStat):
	transaction: Transaction
	list: TasksResponsePayload

class TaskTagsResponse(OkStat):
	transaction: Transaction
	list: TasksTagsResponsePayload

class TaskId(BaseModel):
	id: str

class TasksGetListPayload(BaseModel):
	rev: str
	list: Optional[list[RTMGenericListId]]

class TasksGetListResponse(OkStat):
	tasks: TasksGetListPayload

class TagObject(BaseModel):
	name: str

class TagForList(BaseModel):
	tag: list[TagObject]

class TagsGetListResponse(OkStat):
	tags: TagForList

class DateFormatEnum(IntEnum):
	European = 0
	American = 1

class TimeFormatEnum(IntEnum):
	Format12Hour = 0
	Format24Hour = 1

class SettingsGetListPayload(BaseModel):
	timezone: str
	dateformat: DateFormatEnum # 0 for Euro format, 1 for US format
	timeformat: TimeFormatEnum # 0 for 12-hour format, 1 for 24-hour format
	defaultlist: str
	language: str
	defaultduedate: str
	pro: bool

class SettingsGetListResponse(OkStat):
	settings: SettingsGetListPayload

# class TaskListResponse(OkStat):

# class TaskListResponseOrFail(BaseModel):
# 	rsp: Union[TaskListResponse, FailStat]

class Response(BaseModel):
	rsp: Union[AuthCheckTokenResponse, ListsGetListResponse, TestEchoResponse, FailStat]
