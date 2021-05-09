from enum import Enum
from typing import Union

from pydantic import BaseModel, constr, validator

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

class Response(BaseModel):
	rsp: Union[AuthCheckTokenResponse, ListsGetListResponse, TestEchoResponse, FailStat]
