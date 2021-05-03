from logging import info
from rtm import Task

def test_basic(api, task):
	from pprint import pformat
	info(pformat(task))
	parsedTask = Task(**task['list']['taskseries'][0]['task'][0])
	info(parsedTask)
