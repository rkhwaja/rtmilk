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
