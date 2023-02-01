from datetime import date
from logging import getLogger
from typing import Generic, List, Optional, TypeVar

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

	def _LoadValue(self, value: List[str]):
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

class TagsProperty(_Property[List[str]]):
	def Set(self, value: List[str]):
		task = self._task
		client = task._client
		client.api.TasksSetTags(timeline=self._task._client.timeline,
								list_id=self._task._listId,
								taskseries_id=self._task._taskSeriesId,
								task_id=self._task._taskId,
								tags=value)

	async def SetAsync(self, value: List[str]):
		task = self._task
		client = task._client
		await client.apiAsync.TasksSetTags(timeline=self._task._client.timeline,
								list_id=self._task._listId,
								taskseries_id=self._task._taskSeriesId,
								task_id=self._task._taskId,
								tags=value)

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

class DateProperty(_Property[Optional[date]]):
	def __init__(self, task, dateType):
		super().__init__(task)
		self._dateType = dateType

	def _Parameters(self):
		return {
			'timeline': self._task._client.timeline,
			'list_id': self._task._listId,
			'taskseries_id': self._task._taskSeriesId,
			'task_id': self._task._taskId
		}

	# TODO can just make this Set and don't need to override in derived classes
	def _Set(self, value: Optional[date]):
		parameters = self._Parameters()
		if value is None:
			(self.__class__.F)(self._task._client.api, **parameters) # pylint: disable=no-member
		else:
			parameters[self._dateType] = value
			parameters[f'has_{self._dateType}_time'] = False
			_log.info(f'{parameters=}')
			(self.__class__.F)(self._task._client.api, **parameters) # pylint: disable=no-member

	async def _SetAsync(self, value: Optional[date]):
		parameters = self._Parameters()
		if value is None:
			await (self.__class__.FA)(self._task._client.apiAsync, **parameters) # pylint: disable=no-member
		else:
			parameters[self._dateType] = value
			parameters[f'has_{self._dateType}_time'] = False
			await (self.__class__.FA)(self._task._client.apiAsync, **parameters) # pylint: disable=no-member

class StartDateProperty(DateProperty):
	"""None means no start date"""
	def __init__(self, task):
		super().__init__(task, 'start')
		self.__class__.F = staticmethod(API.TasksSetStartDate)
		_log.info(f'{self.__class__.F=}')
		self.__class__.FA = APIAsync.TasksSetStartDate
		_log.info(f'{API.TasksSetStartDate=}')

	def Set(self, value: Optional[date]):
		super()._Set(value)

	async def SetAsync(self, value: Optional[date]):
		await super()._SetAsync(value)

class DueDateProperty(DateProperty):
	"""None means no due date"""
	def __init__(self, task):
		super().__init__(task, 'due')
		self.__class__.F = staticmethod(API.TasksSetDueDate)
		self.__class__.FA = APIAsync.TasksSetDueDate

	def Set(self, value: Optional[date]):
		super()._Set(value)

	async def SetAsync(self, value: Optional[date]):
		await super()._SetAsync(value)

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
