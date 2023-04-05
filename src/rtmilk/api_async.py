from datetime import date, datetime
from json import loads
from logging import getLogger
from typing import Optional, Union

from aiohttp import ClientResponseError, ClientSession
from pydantic import stricturl, validate_arguments # pylint: disable=no-name-in-module

from .api_base import RTMError, UnauthorizedAPIBase
from .models import AuthResponse, EchoResponse, ListsResponse, NotesResponse, PriorityDirectionEnum, PriorityEnum, SettingsResponse, SingleListResponse, SubscriptionListResponse, SubscriptionResponse, TagListResponse, TaskListResponse, TaskPayload, TaskResponse, TimelineResponse, TopicListResponse
from .sansio import AuthCheckToken, AuthGetFrob, AuthGetToken, ListsAdd, ListsArchive, ListsDelete, ListsGetList, ListsSetDefaultList, ListsSetName, ListsUnarchive, PushGetSubscriptions, PushGetTopics, PushSubscribe, PushUnsubscribe, TagsGetList, TasksAdd, TasksAddTags, TasksComplete, TasksDelete, TasksGetList, TasksMovePriority, TasksNotesAdd, TasksRemoveTags, TasksSetDueDate, TasksSetName, TasksSetPriority, TasksSetStartDate, TasksSetTags, TasksUncomplete, TestEcho, TimelinesCreate, SettingsGetList, REST_URL
from .secrets import SecretsWithAuthorization

_log = getLogger(__name__)

async def _CallAsync(params):
	try:
		async with ClientSession() as session:
			async with session.get(REST_URL, params=params) as resp:
				text = await resp.text()
				return loads(text)['rsp']
	except (ClientResponseError, ValueError) as e:
		raise RTMError() from e

class UnauthorizedAPIAsync(UnauthorizedAPIBase):
	"""Async wrappers for API calls that don't need authorization"""

	async def TestEcho(self, **params) -> EchoResponse:
		rsp = await _CallAsync(TestEcho(self._secrets).In(**params))
		return TestEcho.Out(**rsp)

	async def AuthGetFrob(self) -> str:
		return AuthGetFrob.Out(** await _CallAsync(AuthGetFrob(self._secrets).In()))

	@validate_arguments
	async def AuthGetToken(self, frob: str) -> str:
		return AuthGetToken.Out(** await _CallAsync(AuthGetToken(self._secrets).In(frob)))

	@validate_arguments
	async def AuthCheckToken(self, auth_token: str) -> AuthResponse:
		return AuthCheckToken.Out(** await _CallAsync(AuthCheckToken(self._secrets).In(auth_token)))

class APIAsync(UnauthorizedAPIAsync):
	"""Async wrappers for all API calls"""

	def __init__(self, apiKey, sharedSecret, token):
		super().__init__(apiKey, sharedSecret)
		self._authSecrets = SecretsWithAuthorization(apiKey, sharedSecret, token)

	@property
	def secrets(self):
		return self._authSecrets

	@validate_arguments
	async def ListsAdd(self, timeline: str, name: str, filter: Optional[str] = None) -> SingleListResponse: # pylint: disable=redefined-builtin
		return ListsAdd.Out(** await _CallAsync(ListsAdd(self._authSecrets).In(timeline=timeline, name=name, filter=filter)))

	@validate_arguments
	async def ListsArchive(self, timeline: str, list_id: str) -> SingleListResponse:
		return ListsArchive.Out(** await _CallAsync(ListsArchive(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	@validate_arguments
	async def ListsDelete(self, timeline: str, list_id: str) -> SingleListResponse:
		return ListsDelete.Out(** await _CallAsync(ListsDelete(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	async def ListsGetList(self) -> ListsResponse:
		return ListsGetList.Out(** await _CallAsync(ListsGetList(self._authSecrets).In()))

	@validate_arguments
	async def ListsSetDefaultList(self, timeline: str, list_id: str) -> None:
		return ListsSetDefaultList.Out(** await _CallAsync(ListsSetDefaultList(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	@validate_arguments
	async def ListsSetName(self, timeline: str, list_id: str, name: str) -> SingleListResponse:
		return ListsSetName.Out(** await _CallAsync(ListsSetName(self._authSecrets).In(timeline=timeline, list_id=list_id, name=name)))

	@validate_arguments
	async def ListsUnarchive(self, timeline: str, list_id: str) -> SingleListResponse:
		return ListsUnarchive.Out(** await _CallAsync(ListsUnarchive(self._authSecrets).In(timeline=timeline, list_id=list_id)))

	async def PushGetSubscriptions(self) -> SubscriptionListResponse:
		return PushGetSubscriptions.Out(** await _CallAsync(PushGetSubscriptions(self._authSecrets).In()))

	async def PushGetTopics(self) -> TopicListResponse:
		return PushGetTopics.Out(** await _CallAsync(PushGetTopics(self._authSecrets).In()))

	@validate_arguments
	async def PushSubscribe(self, url: stricturl(allowed_schemes='https'), topics: str, push_format: str, timeline: str, lease_seconds: Optional[int] = None, filter: Optional[str] = None) -> SubscriptionResponse: # pylint: disable=redefined-builtin
		return PushSubscribe.Out(** await _CallAsync(PushSubscribe(self._authSecrets).In(url=url, topics=topics, push_format=push_format, timeline=timeline, lease_seconds=lease_seconds, filter=filter)))

	@validate_arguments
	async def PushUnsubscribe(self, timeline: str, subscription_id: str) -> None:
		return PushUnsubscribe.Out(** await _CallAsync(PushUnsubscribe(self._authSecrets).In(timeline=timeline, subscription_id=subscription_id)))

	async def TimelinesCreate(self) -> TimelineResponse:
		return TimelinesCreate.Out(** await _CallAsync(TimelinesCreate(self._authSecrets).In()))

	async def SettingsGetList(self) -> SettingsResponse:
		return SettingsGetList.Out(** await _CallAsync(SettingsGetList(self._authSecrets).In()))

	async def TagsGetList(self) -> TagListResponse:
		return TagsGetList.Out(** await _CallAsync(TagsGetList(self._authSecrets).In()))

	@validate_arguments
	async def TasksAdd(self, timeline: str, name: str, list_id: Optional[str] = None, parse: Optional[bool] = None, parent_task_id: Optional[str] = None, external_id: Optional[str] = None) -> TaskResponse:
		return TasksAdd.Out(** await _CallAsync(TasksAdd(self._authSecrets).In(timeline=timeline, name=name, list_id=list_id, parse=parse, parent_task_id=parent_task_id, external_id=external_id)))

	@validate_arguments
	async def TasksAddTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: list[str]) -> TaskResponse:
		return TasksAddTags.Out(** await _CallAsync(TasksAddTags(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)))

	@validate_arguments
	async def TasksComplete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str) -> TaskResponse:
		return TasksComplete.Out(** await _CallAsync(TasksComplete(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)))

	@validate_arguments
	async def TasksUncomplete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str) -> TaskResponse:
		return TasksUncomplete.Out(** await _CallAsync(TasksUncomplete(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)))

	@validate_arguments
	async def TasksDelete(self, timeline: str, list_id: str, taskseries_id: str, task_id: str) -> TaskResponse:
		return TasksDelete.Out(** await _CallAsync(TasksDelete(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)))

	@validate_arguments
	async def TasksGetList(self, list_id: Optional[str] = None, filter: Optional[str] = None, last_sync: Optional[datetime] = None) -> TaskListResponse: # pylint: disable=redefined-builtin
		return TasksGetList.Out(** await _CallAsync(TasksGetList(self._authSecrets).In(list_id=list_id, filter=filter, last_sync=last_sync)))

	@validate_arguments
	async def TasksMovePriority(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, direction: PriorityDirectionEnum) -> TaskResponse:
		return TasksMovePriority.Out(** await _CallAsync(TasksMovePriority(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, direction=direction)))

	@validate_arguments
	async def TasksNotesAdd(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, note_title: str, note_text: str) -> NotesResponse:
		return TasksNotesAdd.Out(** await _CallAsync(TasksNotesAdd(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, note_title=note_title, note_text=note_text)))

	@validate_arguments
	async def TasksRemoveTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: list[str]) -> TaskResponse:
		return TasksRemoveTags.Out(** await _CallAsync(TasksRemoveTags(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)))

	@validate_arguments
	async def TasksSetDueDate(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, due: Union[date, datetime, str, None]=None, has_due_time: Optional[bool] = None, parse: Optional[bool] = None) -> TaskResponse:
		return TasksSetDueDate.Out(** await _CallAsync(TasksSetDueDate(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, due=due, has_due_time=has_due_time, parse=parse)))

	@validate_arguments
	async def TasksSetName(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, name: str) -> TaskResponse:
		return TasksSetName.Out(** await _CallAsync(TasksSetName(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, name=name)))

	@validate_arguments
	async def TasksSetPriority(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, priority: Optional[PriorityEnum	] = None) -> TaskPayload:
		return TasksSetPriority.Out(** await _CallAsync(TasksSetPriority(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, priority=priority)))

	@validate_arguments
	async def TasksSetStartDate(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, start: Union[date, datetime, str, None] = None, has_start_time: Optional[bool] = None, parse: Optional[bool] = None) -> TaskResponse:
		return TasksSetStartDate.Out(** await _CallAsync(TasksSetStartDate(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, start=start, has_start_time=has_start_time, parse=parse)))

	@validate_arguments
	async def TasksSetTags(self, timeline: str, list_id: str, taskseries_id: str, task_id: str, tags: Optional[list[str]] = None) -> TaskResponse:
		return TasksSetTags.Out(** await _CallAsync(TasksSetTags(self._authSecrets).In(timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)))
