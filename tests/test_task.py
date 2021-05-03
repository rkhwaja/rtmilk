from logging import info
from pprint import pformat

from rtm import Task, TaskSeries

def test_basic(task):
	info(pformat(task))
	parsedTask = Task(**task['list']['taskseries'][0]['task'][0])
	info(parsedTask)

	parsedTaskSeries = TaskSeries(**task['list']['taskseries'][0])
	info(parsedTaskSeries)
