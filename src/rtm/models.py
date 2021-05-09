from typing import Union

from pydantic import constr, BaseModel

class RTMError2(BaseModel):
	code: int
	msg: str

class TestEchoResponse(BaseModel):
	stat: constr(regex='ok')
	method: constr(regex='rtm.test.echo')

class RTMList(BaseModel):
	id: int
	name: str
	deleted: bool
	locked: bool
	archived: bool
	position: int
	smart: bool

class RTMSmartList(BaseModel):
	id: int
	name: str
	deleted: bool
	locked: bool
	archived: bool
	position: int
	smart: bool
	filter: str

class List(BaseModel):
	list: list[Union[RTMSmartList, RTMList]]

class ListsGetListResponse(BaseModel):
	stat: constr(regex='ok')
	method: constr(regex='rtm.lists.getList')
	lists: List

class OkStat(BaseModel):
	stat: constr(regex='ok')

class FailStat(BaseModel):
	stat: constr(regex='fail')
	err: RTMError2

class Response(BaseModel):
	rsp: Union[ListsGetListResponse, TestEchoResponse, OkStat, FailStat]
