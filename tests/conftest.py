from os import environ
from unittest.mock import MagicMock
from uuid import uuid4

from pytest import fixture

from rtmilk import API, APIAsync, CreateClient

try:
	from dotenv import load_dotenv
	load_dotenv()
	print('.env imported')
except ImportError:
	pass

def _GetConfig():
	if 'RTM_TOKEN' in environ:
		return (environ['RTM_API_KEY'], environ['RTM_SHARED_SECRET'], environ['RTM_TOKEN'])
	with open('rtm-token.txt', encoding='utf-8') as f:
		token = f.read()
	return (environ['RTM_API_KEY'], environ['RTM_SHARED_SECRET'], token)

@fixture(scope='session')
def api():
	apiKey, sharedSecret, token = _GetConfig()
	return API(apiKey, sharedSecret, token)

@fixture(scope='session')
def apiAsync():
	apiKey, sharedSecret, token = _GetConfig()
	return APIAsync(apiKey, sharedSecret, token)

@fixture
def timeline(api):
	return api.TimelinesCreate().timeline

@fixture
def task(api, timeline):
	task = api.TasksAdd(timeline, f'new task {uuid4()}')
	yield task
	api.TasksDelete(
		timeline, task.list.id,
		task.list.taskseries[0].id,
		task.list.taskseries[0].task[0].id)

@fixture
def newList(api, timeline):
	list_ = api.ListsAdd(timeline, f'list {uuid4()}')
	yield list_
	list_ = api.ListsDelete(timeline, list_.list.id)
	assert list_.list.deleted is True, list_

@fixture
def newSmartList(api, timeline):
	list_ = api.ListsAdd(timeline, f'list {uuid4()}', filter='tag:tag1')
	yield list_
	list_ = api.ListsDelete(timeline, list_.list.id)
	assert list_.list.deleted is True, list_

class TaskCreator:
	def __init__(self, client_):
		self.client = client_
		self.tasks = []

	def Add(self, name):
		task_ = self.client.Add(name)
		self.tasks.append(task_)
		return task_

	def Cleanup(self):
		for task in self.tasks:
			task.Delete()
		self.tasks.clear()

class TaskCreatorAPI:
	def __init__(self, api, timeline):
		self.api = api
		self.timeline = timeline
		self.tasks = []

	def Add(self, name):
		task = self.api.TasksAdd(self.timeline, name)
		self.tasks.append(task)
		return task

	def Cleanup(self):
		for task in self.tasks:
			self.api.TasksDelete(
				self.timeline, task.list.id,
				task.list.taskseries[0].id,
				task.list.taskseries[0].task[0].id)
		self.tasks.clear()

@fixture
def taskCreatorAPI(api, timeline):
	creator = TaskCreatorAPI(api, timeline)
	yield creator
	creator.Cleanup()

@fixture
def taskCreator(client):
	creator = TaskCreator(client)
	yield creator
	creator.Cleanup()

@fixture
def client():
	apiKey, sharedSecret, token = _GetConfig()
	return CreateClient(apiKey, sharedSecret, token)

@fixture
def mockClient():
	return MagicMock()
