from __future__ import annotations

from datetime import datetime
from logging import getLogger

from pydantic import validate_call

from .api_async import APIAsync
from .api_sync import API
from ._properties import CompleteProperty, DueDateProperty, NameProperty, NotesProperty, StartDateProperty, TagsProperty

_log = getLogger(__name__)

class Task:
	"""Represents an RTM task"""

	def __init__(self, client, listId, taskSeriesId, taskId):
		self._client = client
		self._listId = listId
		self._taskSeriesId = taskSeriesId
		self._taskId = taskId

		self.name = NameProperty(self)
		self.tags = TagsProperty(self)
		self.startDate = StartDateProperty(self)
		self.dueDate = DueDateProperty(self)
		self.complete = CompleteProperty(self)
		self.notes = NotesProperty(self)
		self.createTime: datetime | None = None
		self.modifiedTime: datetime | None = None

	def __repr__(self):
		return f'Task({self.name.value})'

	@validate_call
	def Delete(self):
		_log.info(f'{self}.Delete')
		self._client.api.TasksDelete(timeline=self._client.timeline,
								list_id=self._listId,
								taskseries_id=self._taskSeriesId,
								task_id=self._taskId)

	@validate_call
	async def DeleteAsync(self):
		_log.info(f'{self}.DeleteAsync')
		await self._client.apiAsync.TasksDelete(timeline=self._client.timeline,
								list_id=self._listId,
								taskseries_id=self._taskSeriesId,
								task_id=self._taskId)

# Serialize python datetime object to string for use by filters
def FilterDate(date_):
	return datetime.strftime(date_, '%m/%d/%Y')

def _CreateFromTaskSeries(client, listId, taskSeries):
	_log.info(f'{taskSeries=}')
	task0 = taskSeries.task[0]
	result = Task(client, listId, taskSeries.id, task0.id)

	result.name._LoadValue(taskSeries.name)
	result.tags._LoadValue(set(taskSeries.tags.tag) if hasattr(taskSeries.tags, 'tag') else set(taskSeries.tags))
	result.startDate._LoadValue(task0.start.date() if task0.start is not None else None) # None means no change
	result.dueDate._LoadValue(task0.due.date() if task0.due is not None else None) # None means no change
	result.complete._LoadValue(task0.completed is not None)
	result.notes._LoadValue([] if isinstance(taskSeries.notes, list) else taskSeries.notes.note)
	result.createTime = taskSeries.created
	result.modifiedTime = taskSeries.modified

	return result

def _CreateListOfTasks(client, listResponse):
	if listResponse.tasks.list is None:
		return []
	tasks = []
	for list_ in listResponse.tasks.list:
		if not hasattr(list_, 'taskseries') or list_.taskseries is None:
			continue
		tasks.extend([_CreateFromTaskSeries(client, listId=list_.id, taskSeries=ts) for ts in list_.taskseries])
	return tasks

class Client:
	"""Wraps the timeline and adds convenience functions to add and query tasks"""

	@classmethod
	def Create(cls, clientId, clientSecret, token):
		client = Client(clientId, clientSecret, token)
		client._CreateTimeline()
		return client

	@classmethod
	async def CreateAsync(cls, clientId, clientSecret, token):
		client = Client(clientId, clientSecret, token)
		await client._CreateTimelineAsync()
		return client

	def __init__(self, clientId, clientSecret, token):
		self.api = API(clientId, clientSecret, token)
		self.apiAsync = APIAsync(clientId, clientSecret, token)
		self.timeline = None

	def __repr__(self):
		return 'Client()'

	def _CreateTimeline(self):
		self.timeline = self.api.TimelinesCreate().timeline

	async def _CreateTimelineAsync(self):
		self.timeline = await self.apiAsync.TimelinesCreate().timeline

	@validate_call
	def Get(self, filter_: str, lastSync: datetime | None = None) -> list[Task]:
		_log.info(f'Get: {filter_}, {lastSync}')
		listResponse = self.api.TasksGetList(filter=filter_, last_sync=lastSync)
		return _CreateListOfTasks(self, listResponse)

	@validate_call
	def Add(self, name: str) -> Task:
		_log.info(f'Add: {name}')
		taskResponse = self.api.TasksAdd(self.timeline, name)
		return _CreateFromTaskSeries(self, listId=taskResponse.list.id, taskSeries=taskResponse.list.taskseries[0])

	@validate_call
	async def GetAsync(self, filter_: str, lastSync: datetime | None = None) -> list[Task]:
		_log.info(f'GetAsync: {filter_}, {lastSync}')
		listResponse = await self.apiAsync.TasksGetList(filter=filter_, last_sync=lastSync)
		return _CreateListOfTasks(self, listResponse)

	@validate_call
	async def AddAsync(self, name: str) -> Task:
		_log.info(f'AddAsync: {name}')
		taskResponse = await self.apiAsync.TasksAdd(self.timeline, name)
		return _CreateFromTaskSeries(self, listId=taskResponse.list.id, taskSeries=taskResponse.list.taskseries[0])
