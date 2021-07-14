from datetime import date

from rtmilk import And, Due, NameIs, Or, Priority, PriorityEnum, Status

def testFilterString():
	assert And(NameIs('the-name'), Status(True)).Text() == '(name:"the-name") AND (status:completed)'

	assert Or(Priority(PriorityEnum.Priority1), NameIs('the-name')).Text() == '(priority:1) OR (name:"the-name")'

def testFilterSearch(client, taskCreator):
	_ = taskCreator.Add('task1')
	task2 = taskCreator.Add('task2')

	tasks = client.Get(NameIs('task1').Text())
	assert len(tasks) == 1 and tasks[0].name.value == 'task1'

	today = date.today()
	task2.dueDate.Set(today)

	tasks = client.Get(Or(NameIs('task1'), Due(today)).Text())
	assert len(tasks) == 2
