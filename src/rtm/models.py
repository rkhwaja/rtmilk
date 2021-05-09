from datetime import datetime
from enum import Enum
from typing import Literal, Union

from pydantic import AnyHttpUrl, BaseModel, constr, validator

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
	method: constr(regex='rtm.test.echo')

class RTMGenericList(BaseModel):
	id: int
	name: str
	deleted: bool
	locked: bool
	archived: bool
	position: int

class RTMList(RTMGenericList):
	smart: bool # TODO - split on whether this is true or false

	@validator('smart')
	def NotASmartList(cls, value: bool) -> bool:
		if value is not False:
			raise ValueError('must be False for non-smart lists')
		return value

class RTMSmartList(RTMList):
	smart: bool
	filter: str

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
	priority: Literal['N', '1', '2', '3']
	start: Union[EmptyStrToNone[datetime]]

class TaskSeries(BaseModel):
	id: str
	created: datetime
	modified: datetime
	name: str
	source: str
	url: EmptyStrToNone[AnyHttpUrl]
	location_id: str
	tags: list[str]
	participants: list[str]
	notes: list[str]
	task: list[Task]

class TasksResponsePayload(BaseModel):
	id: str
	taskseries: list[TaskSeries]

class Transaction(BaseModel):
	id: str
	undoable: bool

class TasksResponse(OkStat):
	transaction: Transaction
	list:  TasksResponsePayload

class SettingsGetListPayload(BaseModel):
	timezone: str
	dateformat: int # 0 for Euro format, 1 for US format
	timeformat: int # 0 for 12-hour format, 1 for 24-hour format
	defaultlist: str
	language: str
	defaultduedate: str
	pro: bool

class SettingsGetListResponse(OkStat):
	settings: SettingsGetListPayload

class Response(BaseModel):
	rsp: Union[AuthCheckTokenResponse, ListsGetListResponse, TestEchoResponse, FailStat]
