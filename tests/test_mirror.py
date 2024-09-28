from datetime import datetime, timedelta

from rtmilk import Mirror, TaskData

def testMirror(mockClient):
	Mirror(mockClient, [], [TaskData('name')])

def test_ChangeTagsOnTaskBeforeStart(client, taskCreator):
	name = 'rtmilk test ChangeTagsOnTaskBeforeStart'
	task = taskCreator.Add(name)
	task.startDate.Set(datetime.today() + timedelta(days=2))
	task.tags.Set({'rtmilk-test-tag1', 'rtmilk-test-tag2'})
	task.complete.Set(True)

	tasks = client.Get(f'name: {name}')
	assert len(tasks) == 1
	task = tasks[0]

	taskData = TaskData.FromTask(task)
	taskData.tags -= {'rtmilk-test-tag1'}
	Mirror(client, [task], [taskData])

	tasks = client.Get(f'name: {name}')
	assert len(tasks) == 1
	assert tasks[0].tags.value == {'rtmilk-test-tag2'}
