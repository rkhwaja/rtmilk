from datetime import datetime
from hashlib import md5
from logging import getLogger
from pprint import pformat
from typing import List

from pydantic import stricturl, validate_arguments, ValidationError

from .models import AuthResponse, EchoResponse, FailStat, ListsResponse, NotesResponse, PriorityDirectionEnum, RTMError, SettingsResponse, SingleListResponse, SubscriptionListResponse, SubscriptionResponse, TagListResponse, TaskListResponse, TaskPayload, TaskResponse, TimelineResponse, TopicListResponse

REST_URL = 'https://api.rememberthemilk.com/services/rest/'

_log = getLogger('rtmilk')

def _CheckKwargs(keywordArgs, allowedArgs):
	for name, _ in keywordArgs.items():
		if name not in allowedArgs:
			raise TypeError(f'{name} is an unexpected keyword argument')

def _RtmDate(date_):
	"""Serialize python datetime object to string for use by main "set" API functions"""
	return datetime(date_.year, date_.month, date_.day, hour=8).isoformat()

def _ValidateReturn(type_, rsp):
	try:
		_log.debug(f'Parsing {type_}:\n{pformat(rsp)}')
		return type_(**rsp)
	except ValidationError as e:
		_log.error(f'Failed to validate against {type_}:\n{pformat(rsp)}\n{e}')
		failStat = FailStat(**rsp)
		raise RTMError(failStat.err.code, failStat.err.msg) from e

def ApiSig(sharedSecret, params):
	sortedItems = sorted(params.items(), key=lambda x: x[0])
	concatenatedParams = ''.join((key + value for key, value in sortedItems))
	return md5((sharedSecret + concatenatedParams).encode()).hexdigest()

# the return parsing is the same for authorized and unauthorized calls
# the signing of parameters is different for authorized and unauthorized calls
# want to only allow calls when authorized i.e. enforce it via inherited types
# want to share the implementation of the sig calculations etc at the sansio level
# both sync and async api classes share the same (un)authorized base classes so that you can call unauthorized even if you're authorized
# the base classes just have different constructors which do or don't take a token
# the base classes put their parameters into a secrets object which then implements the signing functions

# no need to store the secrets in the call object itself, they're only used in the "In" call

class Call:
	def __init__(self, secrets):
		self._secrets = secrets

	def CommonParams(self, method, **params):
		return self._secrets.SignParams(method, **params)

# don't do the 2 different base classes here, rely on the API objects to do it
UnauthorizedCall = Call

class TestEcho(UnauthorizedCall):
	def In(self, **params):
		return self.CommonParams('rtm.test.echo', **params)

	@classmethod
	def Out(cls, **rsp):
		return EchoResponse(**rsp)

class AuthGetFrob(UnauthorizedCall):
	def In(self):
		return self.CommonParams('rtm.auth.getFrob')

	@classmethod
	def Out(cls, **rsp):
		return rsp['frob']

class AuthGetToken(UnauthorizedCall):
	@validate_arguments
	def In(self, frob: str) -> str:
		return self.CommonParams('rtm.auth.getToken', frob=frob)

	@classmethod
	def Out(cls, **rsp):
		return rsp['auth']['token']

class AuthCheckToken(UnauthorizedCall):
	@validate_arguments
	def In(self, auth_token: str):
		return self.CommonParams('rtm.auth.checkToken', auth_token=auth_token)

	@classmethod
	def Out(cls, **rsp):
		return AuthResponse(**rsp)

AuthorizedCall = Call

class ListsAdd(AuthorizedCall):
	def In(self, timeline: str, name: str, **kwargs):
		_CheckKwargs(kwargs, ['filter']) # TODO validate parameter
		return self.CommonParams('rtm.lists.add', timeline=timeline, name=name, **kwargs)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(SingleListResponse, rsp)

class ListsArchive(AuthorizedCall):
	@validate_arguments
	def In(self, timeline: str, list_id: str):
		return self.CommonParams('rtm.lists.archive', timeline=timeline, list_id=list_id)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(SingleListResponse, rsp)

class ListsDelete(AuthorizedCall):
	@validate_arguments
	def In(self, timeline: str, list_id: str):
		return self.CommonParams('rtm.lists.delete', timeline=timeline, list_id=list_id)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(SingleListResponse, rsp)

class ListsGetList(AuthorizedCall):
	def In(self):
		return self.CommonParams('rtm.lists.getList')

	@classmethod
	def Out(cls, **rsp):
		return ListsResponse(**rsp)

class ListsSetDefaultList(AuthorizedCall):
	@validate_arguments
	def In(self, timeline: str, list_id: str):
		return self.CommonParams('rtm.lists.setDefaultList', timeline=timeline, list_id=list_id)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(SingleListResponse, rsp)

class ListsSetName(AuthorizedCall):
	@validate_arguments
	def In(self, timeline: str, list_id: str, name: str):
		return self.CommonParams('rtm.lists.setName', timeline=timeline, list_id=list_id, name=name)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(SingleListResponse, rsp)

class ListsUnarchive(AuthorizedCall):
	@validate_arguments
	def In(self, timeline: str, list_id: str):
		return self.CommonParams('rtm.lists.unarchive', timeline=timeline, list_id=list_id)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(SingleListResponse, rsp)

class PushGetSubscriptions(AuthorizedCall):
	def In(self):
		return self.CommonParams('rtm.push.getSubscriptions')

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(SubscriptionListResponse, rsp)

class PushGetTopics(AuthorizedCall):
	def In(self):
		return self.CommonParams('rtm.push.getTopics')

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TopicListResponse, rsp)

class PushSubscribe(AuthorizedCall):
	@validate_arguments
	def In(self, url: stricturl(allowed_schemes='https'), topics: str, push_format: str, timeline: str, **kwargs):
		_CheckKwargs(kwargs, ['lease_seconds', 'filter']) # TODO validate parameters
		return self.CommonParams('rtm.push.subscribe', url=url, topics=topics, push_format=push_format, timeline=timeline, **kwargs)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(SubscriptionResponse, rsp)

class PushUnsubscribe(AuthorizedCall):
	def In(self, timeline: str, subscription_id: str):
		return self.CommonParams('rtm.push.unsubscribe', timeline=timeline, subscription_id=subscription_id)

	@classmethod
	def Out(cls):
		return None

class TimelinesCreate(AuthorizedCall):
	def In(self):
		return self.CommonParams('rtm.timelines.create')

	@classmethod
	def Out(cls, **rsp):
		return TimelineResponse(**rsp)

class SettingsGetList(AuthorizedCall):
	def In(self):
		return self.CommonParams('rtm.settings.getList')

	@classmethod
	def Out(cls, **rsp):
		return SettingsResponse(**rsp)

class TagsGetList(AuthorizedCall):
	def In(self):
		return self.CommonParams('rtm.tags.getList')

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TagListResponse, rsp)

class TasksAdd(AuthorizedCall):
	def In(self, timeline: str, name: str, **kwargs):
		_CheckKwargs(kwargs, ['list_id', 'parse', 'parent_task_id', 'external_id']) # TODO validate parameters
		return self.CommonParams('rtm.tasks.add', timeline=timeline, name=name, **kwargs)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)

class TasksAddTags(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: List[str]):
		# TODO the join here should be done as part of the pydantic parameter validation stuff
		return self.CommonParams('rtm.tasks.addTags', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=','.join(tags))

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)

class TasksComplete(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str):
		return self.CommonParams('rtm.tasks.complete', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)

class TasksDelete(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str):
		return self.CommonParams('rtm.tasks.delete', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)

class TasksGetList(AuthorizedCall):
	def In(self, **kwargs):
		_CheckKwargs(kwargs, ['list_id', 'filter', 'last_sync']) # TODO validate parameters
		return self.CommonParams('rtm.tasks.getList', **kwargs)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskListResponse, rsp)

class TasksMovePriority(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, direction: PriorityDirectionEnum):
		direction = direction.value
		return self.CommonParams('rtm.tasks.movePriority', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, direction=direction)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)

class TasksNotesAdd(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, note_title: str, note_text: str):
		return self.CommonParams('rtm.tasks.notes.add', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, note_title=note_title, note_text=note_text)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(NotesResponse, rsp)

class TasksRemoveTags(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: List[str]):
		tags = ','.join(tags)
		return self.CommonParams('rtm.tasks.removeTags', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)

class TasksSetDueDate(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, **kwargs):
		_CheckKwargs(kwargs, ['due', 'has_due_time', 'parse']) # TODO validate parameters
		if 'has_due_time' in kwargs:
			kwargs['has_due_time'] = '1' if kwargs['has_due_time'] else '0'
		if 'due' in kwargs:
			kwargs['due'] = _RtmDate(kwargs['due'])
		return self.CommonParams('rtm.tasks.setDueDate', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **kwargs)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)

class TasksSetName(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, name: str):
		return self.CommonParams('rtm.tasks.setName', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, name=name)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)

class TasksSetPriority(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, **kwargs):
		_CheckKwargs(kwargs, ['priority']) # TODO validate parameter
		if 'priority' in kwargs:
			kwargs['priority'] = kwargs['priority'].value
		return self.CommonParams('rtm.tasks.setPriority', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **kwargs)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskPayload, rsp['list'])

class TasksSetStartDate(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, **kwargs):
		_CheckKwargs(kwargs, ['start', 'has_start_time', 'parse']) # TODO validate parameter
		if 'has_start_time' in kwargs:
			kwargs['has_start_time'] = '1' if kwargs['has_start_time'] else '0'
		if 'start' in kwargs:
			kwargs['start'] = _RtmDate(kwargs['start'])
		return self.CommonParams('rtm.tasks.setStartDate', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **kwargs)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)

class TasksSetTags(AuthorizedCall):
	def In(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, **kwargs):
		_CheckKwargs(kwargs, ['tags']) # TODO validate parameter
		if 'tags' in kwargs:
			kwargs['tags'] = ','.join(kwargs['tags'])
		return self.CommonParams('rtm.tasks.setTags', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **kwargs)

	@classmethod
	def Out(cls, **rsp):
		return _ValidateReturn(TaskResponse, rsp)
