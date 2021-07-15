from os import environ

from pytest import fixture

from rtmilk import API

try:
	from dotenv import load_dotenv
	load_dotenv()
	print('.env imported')
except ImportError:
	pass

@fixture(scope='session')
def api():
	if 'RTM_TOKEN' in environ:
		return API(environ['RTM_API_KEY'], environ['RTM_SHARED_SECRET'], environ['RTM_TOKEN'])
	with open('rtm-token.txt') as f:
		token = f.read()
	return API(environ['RTM_API_KEY'], environ['RTM_SHARED_SECRET'], token)

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
def taskCreator(api, timeline): # pylint: disable=redefined-outer-name
	creator = TaskCreator(api, timeline)
	yield creator
	creator.Cleanup()
