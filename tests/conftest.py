from os import environ

from pytest import fixture

from rtmilk import API, Client
from rtmilk.api_async import APIAsync

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
def timeline(api): # pylint: disable=redefined-outer-name
	return api.TimelinesCreate().timeline

@fixture
def task(api, timeline): # pylint: disable=redefined-outer-name
	task = api.TasksAdd(timeline, 'new task') # pylint: disable=redefined-outer-name
	yield task
	api.TasksDelete(
		timeline, task.list.id,
		task.list.taskseries[0].id,
		task.list.taskseries[0].task[0].id)

class TaskCreator:
	def __init__(self, client_):
		self.client = client_
		self.tasks = []

	def Add(self, name):
		task_ = self.client.Add(Task.CreateNew(title=name))
		self.tasks.append(task_)
		return task_

class TaskCreatorAPI:
	def __init__(self, api, timeline): # pylint: disable=redefined-outer-name
		self.api = api
		self.timeline = timeline
		self.tasks = []

	def Add(self, name):
		task = self.api.TasksAdd(self.timeline, name) # pylint: disable=redefined-outer-name
		self.tasks.append(task)
		return task

	def Cleanup(self):
		for task in self.tasks: # pylint: disable=redefined-outer-name
			self.api.TasksDelete(
				self.timeline, task.list.id,
				task.list.taskseries[0].id,
				task.list.taskseries[0].task[0].id)
		self.tasks.clear()

@fixture
def taskCreatorAPI(api, timeline): # pylint: disable=redefined-outer-name
	creator = TaskCreatorAPI(api, timeline)
	yield creator
	creator.Cleanup()

@fixture
def client():
	apiKey, sharedSecret, token = _GetConfig()
	return Client(apiKey, sharedSecret, token)
