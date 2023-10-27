from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from listdiff import DiffUnsortedLists
from rtmilk.models import RTMError

@dataclass
class TaskData:
	name: str
	tags: set[str] = field(default_factory=lambda :{})
	startDate: date | datetime = None
	dueDate: date | datetime = None
	notes: str = ''
	complete: bool | None = False # optional here means that either is acceptable i.e. don't change an existing task's complete value

	@classmethod
	def FromTask(cls, task):
		return TaskData(
			name=task.name.value,
			tags=task.tags.value,
			startDate=task.startDate.value,
			dueDate=task.dueDate.value,
			complete=task.complete.value
		)

def _MirrorProperty(property_, value):
	if property_.value != value:
		property_.Set(value)

async def _MirrorPropertyAsync(property_, value):
	if property_.value != value:
		await property_.SetAsync(value)

def _MirrorTask(task, taskData):
	_MirrorProperty(task.tags, taskData.tags)
	try:
		_MirrorProperty(task.startDate, taskData.startDate)
		_MirrorProperty(task.dueDate, taskData.dueDate)
	except RTMError:
		_MirrorProperty(task.dueDate, taskData.dueDate)
		_MirrorProperty(task.startDate, taskData.startDate)
	if taskData.complete is not None:
		_MirrorProperty(task.complete, taskData.complete)

async def _MirrorTaskAsync(task, taskData):
	await _MirrorPropertyAsync(task.tags, taskData.tags)
	try:
		await _MirrorPropertyAsync(task.startDate, taskData.startDate)
		await _MirrorPropertyAsync(task.dueDate, taskData.dueDate)
	except RTMError:
		await _MirrorPropertyAsync(task.dueDate, taskData.dueDate)
		await _MirrorPropertyAsync(task.startDate, taskData.startDate)
	if taskData.complete is not None:
		await _MirrorPropertyAsync(task.complete, taskData.complete)

def Mirror(client, existingTasks, requiredTaskData):
	"""Assumes that there have been no changes since existingTasks were read from the remote
	Won't update a value which was already correct, according to existingTasks"""
	toDelete, matches, toAdd = DiffUnsortedLists(iter(existingTasks), iter(requiredTaskData), lambda x: x.name.value, lambda x: x.name)

	for task in toDelete:
		task.Delete()

	for taskData in toAdd:
		newTask = client.Add(taskData.name)
		if len(taskData.tags) != 0:
			newTask.tags.Set(taskData.tags)
		if taskData.startDate is not None:
			newTask.startDate.Set(taskData.startDate)
		if taskData.dueDate is not None:
			newTask.dueDate.Set(taskData.dueDate)
		if taskData.complete is not False:
			newTask.complete.Set(taskData.complete)
		if taskData.notes != '':
			newTask.notes.Add('', taskData.notes)

	for task, taskData in matches:
		_MirrorTask(task, taskData)

async def MirrorAsync(client, existingTasks, requiredTaskData):
	"""Assumes that there have been no changes since existingTasks were read from the remote
	Won't update a value which was already correct, according to existingTasks"""
	toDelete, matches, toAdd = DiffUnsortedLists(iter(existingTasks), iter(requiredTaskData), lambda x: x.name.value, lambda x: x.name)

	for task in toDelete:
		await task.DeleteAsync()

	for taskData in toAdd:
		newTask = await client.AddAsync(taskData.name)
		if len(taskData.tags) != 0:
			await newTask.tags.SetAsync(taskData.tags)
		if taskData.startDate is not None:
			await newTask.startDate.SetAsync(taskData.startDate)
		if taskData.dueDate is not None:
			await newTask.dueDate.SetAsync(taskData.dueDate)
		if taskData.complete is not False:
			await newTask.complete.SetAsync(taskData.complete)
		if taskData.notes != '':
			await newTask.notes.AddAsync('', taskData.notes)

	for task, taskData in matches:
		await _MirrorTaskAsync(task, taskData)
