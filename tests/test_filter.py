from datetime import date

from rtmilk import And, Due, NameIs, Or, Priority, PriorityEnum, Status

def testFilterString():
	assert And(NameIs('the-name'), Status(True)).Text() == '(name:"the-name") AND (status:completed)'

	assert Or(Priority(PriorityEnum.Priority1), NameIs('the-name')).Text() == '(priority:1) OR (name:"the-name")'

def testFilterSearch(client, taskCreator):
	task1 = taskCreator.Add('task1')
	task2 = taskCreator.Add('task2')

	filter = NameIs('task1')
	tasks = client.Get(filter.Text())
	assert len(tasks) == 1 and tasks[0].title == 'task1'

	today = date.today()
	task2.dueDate = today
	client.Edit(task2)

	filter = Or(NameIs('task1'), Due(today))
	tasks = client.Get(filter.Text())
	assert len(tasks) == 2
