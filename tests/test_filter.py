from datetime import date
from uuid import uuid4

from rtmilk import And, Due, NameIs, Or, Priority, PriorityEnum, Status

def testFilterString():
	assert And(NameIs('the-name'), Status(True)).Text() == '(name:"the-name") AND (status:completed)'

	assert Or(Priority(PriorityEnum.Priority1), NameIs('the-name')).Text() == '(priority:1) OR (name:"the-name")'

def testFilterSearch(client, taskCreator):
	name1 = f'task1 {uuid4()}'
	_ = taskCreator.Add(name1)
	task2 = taskCreator.Add(f'task2 {uuid4()}')

	tasks = client.Get(NameIs(name1).Text())
	assert len(tasks) == 1
	assert tasks[0].name.value == name1

	today = date.today()
	task2.dueDate.Set(today)

	tasks = client.Get(Or(NameIs(name1), Due(today)).Text())
	assert len(tasks) == 2 # noqa: PLR2004
