from datetime import date, datetime
from logging import getLogger
from typing import Generic, Optional, TypeVar, Union

from .api_sync import API
from .api_async import APIAsync

_log = getLogger(__name__)
_T = TypeVar('_T')

class _Property(Generic[_T]):
	_value: Optional[_T]

	def __init__(self, task):
		self._task = task
		self._value = None

	def __repr__(self):
		return f'{self.__class__.__name__}({self._value})'

	def _LoadValue(self, value: _T):
		self._value = value

	@property
	def value(self) -> _T:
		return self._value

class NotesProperty:
	def __init__(self, task):
		self._task = task
		self._value = None

	def _LoadValue(self, value: list[str]):
		self._value = value

	@property
	def value(self) -> _T:
		return self._value

	def Add(self, title: str, text: str):
		self._task._client.api.TasksNotesAdd(
			timeline=self._task._client.timeline,
			list_id=self._task._listId,
			taskseries_id=self._task._taskSeriesId,
			task_id=self._task._taskId,
			note_title=title,
			note_text=text)

	async def AddAsync(self, title: str, text: str):
		await self._task._client.apiAsync.TasksNotesAdd(
			timeline=self._task._client.timeline,
			list_id=self._task._listId,
			taskseries_id=self._task._taskSeriesId,
			task_id=self._task._taskId,
			note_title=title,
			note_text=text)

class TagsProperty(_Property[set[str]]):
	def Set(self, value: set[str]):
		task = self._task
		client = task._client
		client.api.TasksSetTags(timeline=self._task._client.timeline,
								list_id=self._task._listId,
								taskseries_id=self._task._taskSeriesId,
								task_id=self._task._taskId,
								tags=list(value))

	async def SetAsync(self, value: set[str]):
		task = self._task
		client = task._client
		await client.apiAsync.TasksSetTags(timeline=self._task._client.timeline,
								list_id=self._task._listId,
								taskseries_id=self._task._taskSeriesId,
								task_id=self._task._taskId,
								tags=list(value))

class CompleteProperty(_Property[bool]):
	def Set(self, value: bool):
		if value is True:
			self._task._client.api.TasksComplete(
				timeline=self._task._client.timeline,
				list_id=self._task._listId,
				taskseries_id=self._task._taskSeriesId,
				task_id=self._task._taskId)
		else:
			self._task._client.api.TasksUncomplete(
				timeline=self._task._client.timeline,
				list_id=self._task._listId,
				taskseries_id=self._task._taskSeriesId,
				task_id=self._task._taskId)

	async def SetAsync(self, value: bool):
		if value is True:
			await self._task._client.api.TasksComplete(
				timeline=self._task._client.timeline,
				list_id=self._task._listId,
				taskseries_id=self._task._taskSeriesId,
				task_id=self._task._taskId)
		else:
			await self._task._client.api.TasksUncomplete(
				timeline=self._task._client.timeline,
				list_id=self._task._listId,
				taskseries_id=self._task._taskSeriesId,
				task_id=self._task._taskId)

class DateProperty(_Property[Optional[Union[date, datetime]]]):
	def __init__(self, task, dateType):
		super().__init__(task)
		self._dateType = dateType

	def _Parameters(self, value):
		parameters = {
			'timeline': self._task._client.timeline,
			'list_id': self._task._listId,
			'taskseries_id': self._task._taskSeriesId,
			'task_id': self._task._taskId
		}
		if value is not None:
			parameters[self._dateType] = value
			parameters[f'has_{self._dateType}_time'] = isinstance(value, datetime)
		return parameters

	def Set(self, value: Optional[Union[date, datetime]]):
		parameters = self._Parameters(value)
		(self.__class__.F)(self._task._client.api, **parameters) # pylint: disable=no-member

	async def SetAsync(self, value: Optional[Union[date, datetime]]):
		parameters = self._Parameters(value)
		await (self.__class__.FA)(self._task._client.apiAsync, **parameters) # pylint: disable=no-member

class StartDateProperty(DateProperty):
	"""None means no start date"""
	def __init__(self, task):
		super().__init__(task, 'start')
		self.__class__.F = staticmethod(API.TasksSetStartDate)
		self.__class__.FA = APIAsync.TasksSetStartDate

class DueDateProperty(DateProperty):
	"""None means no due date"""
	def __init__(self, task):
		super().__init__(task, 'due')
		self.__class__.F = staticmethod(API.TasksSetDueDate)
		self.__class__.FA = APIAsync.TasksSetDueDate

class NameProperty(_Property[str]):
	def Set(self, value: str):
		self._task._client.api.TasksSetName(timeline=self._task._client.timeline,
								list_id=self._task._listId,
								taskseries_id=self._task._taskSeriesId,
								task_id=self._task._taskId,
								name=value)

	async def SetAsync(self, value: str):
		await self._task._client.api.TasksSetName(timeline=self._task._client.timeline,
								list_id=self._task._listId,
								taskseries_id=self._task._taskSeriesId,
								task_id=self._task._taskId,
								name=value)
