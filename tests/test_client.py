from datetime import date, timedelta
from uuid import uuid4

from rtmilk import Task

def test_client(client):
	existingTasks = client.Get('')
	title = f'title: {uuid4()}'
	startDate = date.today()
	taskToAdd = Task(
		title=title,
		tags=['tag1', 'tag2'],
		startDate=startDate,
		dueDate=startDate + timedelta(days=2),
		complete=False,
		note='note')

	client.Add(taskToAdd)
	tasks = client.Get('')
	assert len(tasks) == 1 + len(existingTasks), tasks
	for task in existingTasks:
		for index in range(len(tasks)): # pylint: disable=consider-using-enumerate
			if task.title == tasks[index].title:
				del tasks[index]
				break
	assert len(tasks) == 1, tasks
	assert tasks[0].title == title
	assert sorted(tasks[0].tags) == ['tag1', 'tag2']
	assert tasks[0].startDate == startDate
	assert tasks[0].dueDate == startDate + timedelta(days=2)
	assert tasks[0].complete is False
	client.Delete(tasks[0])
