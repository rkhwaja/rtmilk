from datetime import date, datetime
from logging import getLogger
from pprint import pformat
from typing import Optional, Union

from pydantic import stricturl, validate_arguments # pylint: disable=no-name-in-module
from requests import get
from requests.exceptions import RequestException

from .api_base import RTMError, UnauthorizedAPIBase
from .models import AuthResponse, EchoResponse, ListsResponse, NotesResponse, PriorityDirectionEnum, PriorityEnum, SettingsResponse, SingleListResponse, SubscriptionListResponse, SubscriptionResponse, TagListResponse, TaskListResponse, TaskPayload, TaskResponse, TimelineResponse, TopicListResponse
from .sansio import AuthCheckToken, AuthGetFrob, AuthGetToken, ListsAdd, ListsArchive, ListsDelete, ListsGetList, ListsSetDefaultList, ListsSetName, ListsUnarchive, PushGetSubscriptions, PushGetTopics, PushSubscribe, PushUnsubscribe, TagsGetList, TasksAdd, TasksAddTags, TasksComplete, TasksDelete, TasksGetList, TasksMovePriority, TasksNotesAdd, TasksRemoveTags, TasksSetDueDate, TasksSetName, TasksSetPriority, TasksSetStartDate, TasksSetTags, TasksUncomplete, TestEcho, TimelinesCreate, SettingsGetList, REST_URL
from .secrets import SecretsWithAuthorization

_log = getLogger(__name__)

def _CallSync(params):
	try:
		json = get(REST_URL, params=params).json() # pylint: disable=missing-timeout
		_log.debug(f'JSON response:\n{pformat(json)}')
		return json['rsp']
	except (RequestException, ValueError) as e:
		raise RTMError() from e

class UnauthorizedAPI(UnauthorizedAPIBase):
	"""Synchronous wrappers for API calls that don't need authorization"""

	def TestEcho(self, **params) -> EchoResponse:
		return TestEcho.Out(**_CallSync(TestEcho(self._secrets).In(**params)))

	def AuthGetFrob(self) -> str:
		return AuthGetFrob.Out(**_CallSync(AuthGetFrob(self._secrets).In()))

	@validate_arguments
	def AuthGetToken(self, frob: str) -> str:
		return AuthGetToken.Out(**_CallSync(AuthGetToken(self._secrets).In(frob)))

	@validate_arguments
	def AuthCheckToken(self, auth_token: str) -> AuthResponse:
		return AuthCheckToken.Out(**_CallSync(AuthCheckToken(self._secrets).In(auth_token)))

# replace self._secrets with the authorized version
# allow to call unauthorized secrets with the same object
class API(UnauthorizedAPI):
	"""
	Low-level API wrapper
	Handles the authorization/authentication token and API signature
	There is (almost) a 1-1 relationship between API calls and public member functions
	Parameter names are the same as the API
	The inputs are python types
	The outputs are parsed into pydantic types, including errors
	Translate API errors into exceptions
	"""

	def __init__(self, apiKey, sharedSecret, token):
		super().__init__(apiKey, sharedSecret)
		self._authSecrets = SecretsWithAuthorization(apiKey, sharedSecret, token)

	@property
	def secrets(self):
		return self._authSecrets

	@validate_arguments
	def ListsAdd(self, timeline: str, name: str, filter: Optional[str] = None) -> SingleListResponse: # pylint: disable=redefined-builtin
		return ListsAdd.Out(**_CallSync(ListsAdd(self._authSecrets).In(timeline=timeline, name=name, filter=filter)))

	@validate_arguments
	def ListsArchive(self, timeline: str, list_id: str) -> SingleListResponse:
		return ListsArchive.Out(**_CallSync(ListsArchive(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	@validate_arguments
	def ListsDelete(self, timeline: str, list_id: str) -> SingleListResponse:
		return ListsDelete.Out(**_CallSync(ListsDelete(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	def ListsGetList(self) -> ListsResponse:
		return ListsGetList.Out(**_CallSync(ListsGetList(self._authSecrets).In()))

	@validate_arguments
	def ListsSetDefaultList(self, timeline: str, list_id: str) -> None:
		return ListsSetDefaultList.Out(**_CallSync(ListsSetDefaultList(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	@validate_arguments
	def ListsSetName(self, timeline: str, list_id: str, name: str) -> SingleListResponse:
		return ListsSetName.Out(**_CallSync(ListsSetName(self._authSecrets).In(timeline=timeline, list_id=list_id, name=name)))

	@validate_arguments
	def ListsUnarchive(self, timeline: str, list_id: str) -> SingleListResponse:
		return ListsUnarchive.Out(**_CallSync(ListsUnarchive(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	def PushGetSubscriptions(self) -> SubscriptionListResponse:
		return PushGetSubscriptions.Out(**_CallSync(PushGetSubscriptions(self._authSecrets).In()))

	def PushGetTopics(self) -> TopicListResponse:
		return PushGetTopics.Out(**_CallSync(PushGetTopics(self._authSecrets).In()))

	@validate_arguments
	def PushSubscribe(self, url: stricturl(allowed_schemes='https'), topics: str, push_format: str, timeline: str, lease_seconds: Optional[int] = None, filter: Optional[str] = None) -> SubscriptionResponse: # pylint: disable=redefined-builtin
		return PushSubscribe.Out(**_CallSync(PushSubscribe(self._authSecrets).In(url=url, topics=topics, push_format=push_format, timeline=timeline, lease_seconds=lease_seconds, filter=filter)))

	@validate_arguments
	def PushUnsubscribe(self, timeline: str, subscription_id: str) -> None:
		return PushUnsubscribe.Out(**_CallSync(PushUnsubscribe(self._authSecrets).In(timeline=timeline, subscription_id=subscription_id)))

	def TimelinesCreate(self) -> TimelineResponse:
		return TimelinesCreate.Out(**_CallSync(TimelinesCreate(self._authSecrets).In()))

	def SettingsGetList(self) -> SettingsResponse:
		return SettingsGetList.Out(**_CallSync(SettingsGetList(self._authSecrets).In()))

	def TagsGetList(self) -> TagListResponse:
		return TagsGetList.Out(**_CallSync(TagsGetList(self._authSecrets).In()))

	@validate_arguments
	def TasksAdd(self, timeline: str, name: str, list_id: Optional[str] = None, parse: Optional[bool] = None, parent_task_id: Optional[str] = None, external_id: Optional[str] = None) -> TaskResponse:
		return TasksAdd.Out(**_CallSync(TasksAdd(self._authSecrets).In(timeline=timeline, name=name, list_id=list_id, parse=parse, parent_task_id=parent_task_id, external_id=external_id)))

	@validate_arguments
	def TasksAddTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: list[str]) -> TaskResponse:
		return TasksAddTags.Out(**_CallSync(TasksAddTags(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)))

	@validate_arguments
	def TasksComplete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str) -> TaskResponse:
		return TasksComplete.Out(**_CallSync(TasksComplete(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)))

	@validate_arguments
	def TasksUncomplete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str) -> TaskResponse:
		return TasksUncomplete.Out(**_CallSync(TasksUncomplete(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)))

	@validate_arguments
	def TasksDelete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str) -> TaskResponse:
		return TasksDelete.Out(**_CallSync(TasksDelete(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)))

	@validate_arguments
	def TasksGetList(self, list_id: Optional[str] = None, filter: Optional[str] = None, last_sync: Optional[datetime] = None) -> TaskListResponse: # pylint: disable=redefined-builtin
		return TasksGetList.Out(**_CallSync(TasksGetList(self._authSecrets).In(list_id=list_id, filter=filter, last_sync=last_sync)))

	@validate_arguments
	def TasksMovePriority(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, direction: PriorityDirectionEnum) -> TaskResponse:
		return TasksMovePriority.Out(**_CallSync(TasksMovePriority(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, direction=direction)))

	@validate_arguments
	def TasksNotesAdd(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, note_title: str, note_text: str) -> NotesResponse:
		return TasksNotesAdd.Out(**_CallSync(TasksNotesAdd(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, note_title=note_title, note_text=note_text)))

	@validate_arguments
	def TasksRemoveTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: list[str]) -> TaskResponse:
		return TasksRemoveTags.Out(**_CallSync(TasksRemoveTags(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)))

	@validate_arguments
	def TasksSetDueDate(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, due: Union[date, datetime, str, None] = None, has_due_time: Optional[bool] = None, parse: Optional[bool] = None) -> TaskResponse:
		return TasksSetDueDate.Out(**_CallSync(TasksSetDueDate(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, due=due, has_due_time=has_due_time, parse=parse)))

	@validate_arguments
	def TasksSetName(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, name: str) -> TaskResponse:
		return TasksSetName.Out(**_CallSync(TasksSetName(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, name=name)))

	@validate_arguments
	def TasksSetPriority(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, priority: Optional[PriorityEnum] = None) -> TaskPayload:
		return TasksSetPriority.Out(**_CallSync(TasksSetPriority(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, priority=priority)))

	@validate_arguments
	def TasksSetStartDate(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, start: Union[date, datetime, str, None] = None, has_start_time: Optional[bool] = None, parse: Optional[bool] = None) -> TaskResponse:
		return TasksSetStartDate.Out(**_CallSync(TasksSetStartDate(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, start=start, has_start_time=has_start_time, parse=parse)))

	@validate_arguments
	def TasksSetTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: Optional[list[str]] = None) -> TaskResponse:
		return TasksSetTags.Out(**_CallSync(TasksSetTags(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)))
