from hashlib import md5
from logging import getLogger
from pprint import pformat
from typing import List

from pydantic import AnyHttpUrl, validate_arguments, ValidationError # pylint: disable=no-name-in-module
from requests import get

from .models import AuthResponse, EchoResponse, FailStat, NotesResponse, PriorityDirectionEnum, ListResponse, ListsResponse, SettingsResponse, TagListResponse, TaskPayload, TaskResponse, TimelineResponse

_restUrl = 'https://api.rememberthemilk.com/services/rest/'
_log = getLogger('rtmilk')

class RTMError(Exception):
	def __init__(self, code, message):
		super().__init__(self)
		self.code = code
		self.message = message

	def __repr__(self):
		return f'<RTMError code={self.code}, message={self.message}>'

def _ApiSig(sharedSecret, params):
	sortedItems = sorted(params.items(), key=lambda x: x[0])
	concatenatedParams = ''.join((key + value for key, value in sortedItems))
	return md5((sharedSecret + concatenatedParams).encode()).hexdigest()

def _CheckKwargs(keywordArgs, allowedArgs):
	for name, _ in keywordArgs.items():
		if name not in allowedArgs:
			raise TypeError(f'{name} is an unexpected keyword argument')

def _ValidateReturn(type_, rsp):
	try:
		return type_(**rsp)
	except ValidationError as e:
		_log.error(f'Failed to validate against {type_}:\n{pformat(rsp)}')
		failStat = FailStat(**rsp)
		raise RTMError(failStat.err.code, failStat.err.msg) from e

class API:
	"""
	Low-level API wrapper
	Handles the authorization/authentication token and API signature
	There is (almost) a 1-1 relationship between API calls and public member functions
	Parameter names are the same as the API
	The inputs are python types at the moment
	The outputs are parsed into pydantic types, including errors
	Translate errors into exceptions
	The upper layer will:
	- organize stuff like setting start/due dates in the order that they will be valid
	- hide details like timeline, filter format
	- only send API calls for changed properties
	"""
	def __init__(self, apiKey, sharedSecret, storage):
		self._apiKey = apiKey
		self._sharedSecret = sharedSecret
		self.storage = storage

	@validate_arguments
	def SetToken(self, token: str):
		self.storage.Save(token)

	def _ApiSig(self, params):
		return _ApiSig(self._sharedSecret, params)

	def _MethodParams(self, methodName):
		return {'method': methodName, 'api_key': self._apiKey, 'format': 'json', 'v': '2'}

	def _Call(self, params):
		params['api_sig'] = self._ApiSig(params)
		json = get(_restUrl, params=params).json()
		_log.debug(f'JSON response:\n{pformat(json)}')
		return json['rsp']

	def _CallUnauthorized(self, method, **params):
		_log.debug(f'_CallUnauthorized: {method}, {params}')
		params.update(self._MethodParams(method))
		return self._Call(params)

	def _CallAuthorized(self, method, **params):
		_log.debug(f'_CallAuthorized: {method}, {params}')
		params.update(self._MethodParams(method))
		params.update({'auth_token': self.storage.Load()})
		return self._Call(params)

	def TestEcho(self, **params):
		_log.info(f'Echo: {params}')
		rsp = self._CallUnauthorized('rtm.test.echo', **params)
		return EchoResponse(**rsp)

	def AuthGetFrob(self):
		rsp = self._CallUnauthorized('rtm.auth.getFrob')
		return rsp['frob']

	@validate_arguments
	def AuthGetToken(self, frob: str):
		rsp = self._CallUnauthorized('rtm.auth.getToken', frob=frob)
		return rsp['auth']['token']

	@validate_arguments
	def AuthCheckToken(self, auth_token: str):
		rsp = self._CallUnauthorized('rtm.auth.checkToken', auth_token=auth_token)
		return AuthResponse(**rsp)

	@validate_arguments
	def ListsAdd(self, timeline: str, name: str, **kwargs):
		_CheckKwargs(kwargs, ['filter']) # TODO validate parameter
		rsp = self._CallAuthorized('rtm.lists.add', timeline=timeline, name=name, **kwargs)
		return ListResponse(**rsp)

	@validate_arguments
	def ListsArchive(self, timeline: str, list_id: str):
		rsp = self._CallAuthorized('rtm.lists.archive', timeline=timeline, list_id=list_id)
		return ListResponse(**rsp)

	@validate_arguments
	def ListsDelete(self, timeline: str, list_id: str):
		rsp = self._CallAuthorized('rtm.lists.delete', timeline=timeline, list_id=list_id)
		return ListResponse(**rsp)

	def ListsGetList(self):
		rsp = self._CallAuthorized('rtm.lists.getList')
		return ListsResponse(**rsp)

	@validate_arguments
	def ListsSetDefaultList(self, timeline: str, list_id: str):
		rsp = self._CallAuthorized('rtm.lists.setDefaultList', timeline=timeline, list_id=list_id)
		return ListResponse(**rsp)

	@validate_arguments
	def ListsSetName(self, timeline: str, list_id: str, name: str):
		rsp = self._CallAuthorized('rtm.lists.setName', timeline=timeline, list_id=list_id, name=name)
		return ListResponse(**rsp)

	@validate_arguments
	def ListsUnarchive(self, timeline: str, list_id: str):
		rsp = self._CallAuthorized('rtm.lists.unarchive', timeline=timeline, list_id=list_id)
		return ListResponse(**rsp)

	def PushGetSubscriptions(self):
		return self._CallAuthorized('rtm.push.getSubscriptions')['subscriptions']

	def PushGetTopics(self):
		return self._CallAuthorized('rtm.push.getTopics')['topics']

	@validate_arguments
	def PushSubscribe(self, url: AnyHttpUrl, topics: List[str], push_format, timeline: str, **kwargs):
		_CheckKwargs(kwargs, ['lease_seconds', 'filter']) # TODO validate parameters
		return self._CallAuthorized('rtm.push.subscribe', url=url, topics=topics, push_format=push_format, timeline=timeline, **kwargs)

	@validate_arguments
	def PushUnsubscribe(self, timeline: str, subscription_id: str):
		self._CallAuthorized('rtm.push.unsubscribe', timeline=timeline, subscription_id=subscription_id)

	def TimelinesCreate(self):
		rsp = self._CallAuthorized('rtm.timelines.create')
		return TimelineResponse(**rsp)

	def SettingsGetList(self):
		rsp = self._CallAuthorized('rtm.settings.getList')
		return SettingsResponse(**rsp)

	def TagsGetList(self):
		rsp = self._CallAuthorized('rtm.tags.getList')
		try:
			return TagListResponse(**rsp)
		except ValidationError as e:
			failStat = FailStat(**rsp)
			raise RTMError(failStat.err.code, failStat.err.msg) from e

	@validate_arguments
	def TasksAdd(self, timeline: str, name: str, **kwargs):
		_CheckKwargs(kwargs, ['list_id', 'parse', 'parent_task_id', 'external_id']) # TODO validate parameters
		rsp = self._CallAuthorized('rtm.tasks.add', timeline=timeline, name=name, **kwargs)
		return _ValidateReturn(TaskResponse, rsp)

	@validate_arguments
	def TasksAddTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: List[str]):
		# TODO the join here should be done as part of the pydantic parameter validation stuff
		rsp = self._CallAuthorized('rtm.tasks.addTags', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=','.join(tags))
		return _ValidateReturn(TaskResponse, rsp)

	@validate_arguments
	def TasksComplete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str):
		rsp = self._CallAuthorized('rtm.tasks.complete', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)
		return _ValidateReturn(TaskResponse, rsp)

	@validate_arguments
	def TasksDelete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str):
		rsp = self._CallAuthorized('rtm.tasks.delete', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)
		return _ValidateReturn(TaskResponse, rsp)

	def TasksGetList(self, **kwargs):
		_CheckKwargs(kwargs, ['list_id', 'filter', 'last_sync']) # TODO validate parameters
		rsp = self._CallAuthorized('rtm.tasks.getList', **kwargs)
		return _ValidateReturn(ListResponse, rsp)

	@validate_arguments
	def TasksMovePriority(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, direction: PriorityDirectionEnum):
		direction = direction.value
		rsp = self._CallAuthorized('rtm.tasks.movePriority', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, direction=direction)
		return _ValidateReturn(TaskResponse, rsp)

	@validate_arguments
	def TasksNotesAdd(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, note_title: str, note_text: str):
		rsp = self._CallAuthorized('rtm.tasks.notes.add', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, note_title=note_title, note_text=note_text)
		return _ValidateReturn(NotesResponse, rsp)

	@validate_arguments
	def TasksRemoveTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: List[str]):
		tags = ','.join(tags)
		rsp = self._CallAuthorized('rtm.tasks.removeTags', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)
		return _ValidateReturn(TaskResponse, rsp)

	@validate_arguments
	def TasksSetDueDate(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, **kwargs):
		_CheckKwargs(kwargs, ['due', 'has_due_time', 'parse']) # TODO validate parameters
		rsp = self._CallAuthorized('rtm.tasks.setDueDate', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **kwargs)
		return _ValidateReturn(TaskResponse, rsp)

	@validate_arguments
	def TasksSetName(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, name: str):
		rsp = self._CallAuthorized('rtm.tasks.setName', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, name=name)
		return _ValidateReturn(TaskResponse, rsp)

	@validate_arguments
	def TasksSetPriority(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, **kwargs):
		_CheckKwargs(kwargs, ['priority']) # TODO validate parameter
		if 'priority' in kwargs:
			kwargs['priority'] = kwargs['priority'].value
		rsp = self._CallAuthorized('rtm.tasks.setPriority', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **kwargs)['list']
		return _ValidateReturn(TaskPayload, rsp)

	@validate_arguments
	def TasksSetStartDate(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, **kwargs):
		_CheckKwargs(kwargs, ['start', 'has_start_time', 'parse']) # TODO validate parameter
		rsp = self._CallAuthorized('rtm.tasks.setStartDate', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **kwargs)
		return _ValidateReturn(TaskResponse, rsp)

	@validate_arguments
	def TasksSetTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, **kwargs):
		_CheckKwargs(kwargs, ['tags']) # TODO validate parameter
		if 'tags' in kwargs:
			kwargs['tags'] = ','.join(kwargs['tags'])
		rsp = self._CallAuthorized('rtm.tasks.setTags', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **kwargs)
		return _ValidateReturn(TaskResponse, rsp)
