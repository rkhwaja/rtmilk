from os import environ

from pytest import fixture

from rtm import API, FileStorage

class _EnvironmentVariableStorage:
	def __init__(self, token):
		self.token = token

	def Save(self, token):
		self.token = token

	def Load(self):
		return self.token

@fixture(scope='session')
def api():
	if 'RTM_TOKEN' in environ:
		return API(environ['RTM_API_KEY'], environ['RTM_SHARED_SECRET'], _EnvironmentVariableStorage(environ['RTM_TOKEN']))
	return API(environ['RTM_API_KEY'], environ['RTM_SHARED_SECRET'], FileStorage('rtm-token.json'))

@fixture
def timeline(api): # pylint: disable=redefined-outer-name
	return api.TimelinesCreate()

@fixture
def task(api, timeline): # pylint: disable=redefined-outer-name
	task = api.TasksAdd(timeline, 'new task') # pylint: disable=redefined-outer-name
	yield task
	api.TasksDelete(
		timeline, task['list']['id'],
		task['list']['taskseries'][0]['id'],
		task['list']['taskseries'][0]['task'][0]['id'])
