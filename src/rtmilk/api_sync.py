from __future__ import annotations

from datetime import date, datetime
from logging import getLogger
from pprint import pformat

from pydantic import validate_call
from requests import get
from requests.exceptions import RequestException

from .api_base import RTMError, UnauthorizedAPIBase
from .models import AuthResponse, EchoResponse, ListsResponse, NotesResponse, PriorityDirectionEnum, PriorityEnum, SettingsResponse, SingleListResponse, SubscriptionListResponse, SubscriptionResponse, TagListResponse, TaskListResponse, TaskPayload, TaskResponse, TimelineResponse, TopicListResponse
from ._sansio import AuthCheckToken, AuthGetFrob, AuthGetToken, ListsAdd, ListsArchive, ListsDelete, ListsGetList, ListsSetDefaultList, ListsSetName, ListsUnarchive, PushGetSubscriptions, PushGetTopics, PushSubscribe, PushUnsubscribe, TagsGetList, TasksAdd, TasksAddTags, TasksComplete, TasksDelete, TasksGetList, TasksMovePriority, TasksNotesAdd, TasksRemoveTags, TasksSetDueDate, TasksSetName, TasksSetPriority, TasksSetStartDate, TasksSetTags, TasksUncomplete, TestEcho, TimelinesCreate, SettingsGetList, REST_URL
from ._secrets import SecretsWithAuthorization
from ._utils import HttpsUrl

_log = getLogger(__name__)

def _CallSync(params):
	try:
		response = get(REST_URL, params=params) # noqa: S113
		json = response.json()
		_log.debug(f'JSON response:\n{pformat(json)}')
		return json['rsp']
	except (RequestException, ValueError) as e:
		raise RTMError from e

class UnauthorizedAPI(UnauthorizedAPIBase):
	"""Synchronous wrappers for API calls that don't need authorization"""

	def TestEcho(self, **params) -> EchoResponse:
		return TestEcho.Out(**_CallSync(TestEcho(self._secrets).In(**params)))

	def AuthGetFrob(self) -> str:
		return AuthGetFrob.Out(**_CallSync(AuthGetFrob(self._secrets).In()))

	@validate_call
	def AuthGetToken(self, frob: str) -> str:
		return AuthGetToken.Out(**_CallSync(AuthGetToken(self._secrets).In(frob)))

	@validate_call
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

	@validate_call
	def ListsAdd(self, timeline: str, name: str, filter: str | None = None) -> SingleListResponse:
		return ListsAdd.Out(**_CallSync(ListsAdd(self._authSecrets).In(timeline=timeline, name=name, filter=filter)))

	@validate_call
	def ListsArchive(self, timeline: str, list_id: str) -> SingleListResponse:
		return ListsArchive.Out(**_CallSync(ListsArchive(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	@validate_call
	def ListsDelete(self, timeline: str, list_id: str) -> SingleListResponse:
		return ListsDelete.Out(**_CallSync(ListsDelete(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	def ListsGetList(self) -> ListsResponse:
		return ListsGetList.Out(**_CallSync(ListsGetList(self._authSecrets).In()))

	@validate_call
	def ListsSetDefaultList(self, timeline: str, list_id: str) -> None:
		return ListsSetDefaultList.Out(**_CallSync(ListsSetDefaultList(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	@validate_call
	def ListsSetName(self, timeline: str, list_id: str, name: str) -> SingleListResponse:
		return ListsSetName.Out(**_CallSync(ListsSetName(self._authSecrets).In(timeline=timeline, list_id=list_id, name=name)))

	@validate_call
	def ListsUnarchive(self, timeline: str, list_id: str) -> SingleListResponse:
		return ListsUnarchive.Out(**_CallSync(ListsUnarchive(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	def PushGetSubscriptions(self) -> SubscriptionListResponse:
		return PushGetSubscriptions.Out(**_CallSync(PushGetSubscriptions(self._authSecrets).In()))

	def PushGetTopics(self) -> TopicListResponse:
		return PushGetTopics.Out(**_CallSync(PushGetTopics(self._authSecrets).In()))

	@validate_call
	def PushSubscribe(self, url: HttpsUrl, topics: str, push_format: str, timeline: str, lease_seconds: int | None = None, filter: str | None = None) -> SubscriptionResponse:
		return PushSubscribe.Out(**_CallSync(PushSubscribe(self._authSecrets).In(url=url, topics=topics, push_format=push_format, timeline=timeline, lease_seconds=lease_seconds, filter=filter)))

	@validate_call
	def PushUnsubscribe(self, timeline: str, subscription_id: str) -> None:
		return PushUnsubscribe.Out(**_CallSync(PushUnsubscribe(self._authSecrets).In(timeline=timeline, subscription_id=subscription_id)))

	def TimelinesCreate(self) -> TimelineResponse:
		return TimelinesCreate.Out(**_CallSync(TimelinesCreate(self._authSecrets).In()))

	def SettingsGetList(self) -> SettingsResponse:
		return SettingsGetList.Out(**_CallSync(SettingsGetList(self._authSecrets).In()))

	def TagsGetList(self) -> TagListResponse:
		return TagsGetList.Out(**_CallSync(TagsGetList(self._authSecrets).In()))

	@validate_call
	def TasksAdd(self, timeline: str, name: str, list_id: str | None = None, parse: bool | None = None, parent_task_id: str | None = None, external_id: str | None = None) -> TaskResponse:
		return TasksAdd.Out(**_CallSync(TasksAdd(self._authSecrets).In(timeline=timeline, name=name, list_id=list_id, parse=parse, parent_task_id=parent_task_id, external_id=external_id)))

	@validate_call
	def TasksAddTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: list[str]) -> TaskResponse:
		return TasksAddTags.Out(**_CallSync(TasksAddTags(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)))

	@validate_call
	def TasksComplete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str) -> TaskResponse:
		return TasksComplete.Out(**_CallSync(TasksComplete(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)))

	@validate_call
	def TasksUncomplete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str) -> TaskResponse:
		return TasksUncomplete.Out(**_CallSync(TasksUncomplete(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)))

	@validate_call
	def TasksDelete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str) -> TaskResponse:
		return TasksDelete.Out(**_CallSync(TasksDelete(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)))

	@validate_call
	def TasksGetList(self, list_id: str | None = None, filter: str | None = None, last_sync: datetime | None = None) -> TaskListResponse:
		return TasksGetList.Out(**_CallSync(TasksGetList(self._authSecrets).In(list_id=list_id, filter=filter, last_sync=last_sync)))

	@validate_call
	def TasksMovePriority(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, direction: PriorityDirectionEnum) -> TaskResponse:
		return TasksMovePriority.Out(**_CallSync(TasksMovePriority(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, direction=direction)))

	@validate_call
	def TasksNotesAdd(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, note_title: str, note_text: str) -> NotesResponse:
		return TasksNotesAdd.Out(**_CallSync(TasksNotesAdd(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, note_title=note_title, note_text=note_text)))

	@validate_call
	def TasksRemoveTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: list[str]) -> TaskResponse:
		return TasksRemoveTags.Out(**_CallSync(TasksRemoveTags(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)))

	@validate_call
	def TasksSetDueDate(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, due: date | datetime | str | None = None, has_due_time: bool | None = None, parse: bool | None = None) -> TaskResponse:
		return TasksSetDueDate.Out(**_CallSync(TasksSetDueDate(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, due=due, has_due_time=has_due_time, parse=parse)))

	@validate_call
	def TasksSetName(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, name: str) -> TaskResponse:
		return TasksSetName.Out(**_CallSync(TasksSetName(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, name=name)))

	@validate_call
	def TasksSetPriority(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, priority: PriorityEnum | None = None) -> TaskPayload:
		return TasksSetPriority.Out(**_CallSync(TasksSetPriority(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, priority=priority)))

	@validate_call
	def TasksSetStartDate(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, start: date | datetime | str | None = None, has_start_time: bool | None = None, parse: bool | None = None) -> TaskResponse:
		return TasksSetStartDate.Out(**_CallSync(TasksSetStartDate(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, start=start, has_start_time=has_start_time, parse=parse)))

	@validate_call
	def TasksSetTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: list[str] | None = None) -> TaskResponse:
		return TasksSetTags.Out(**_CallSync(TasksSetTags(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)))
