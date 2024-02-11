from datetime import datetime, timedelta

from rtmilk.mirror import Mirror, TaskData

def testMirror(mockClient):
	Mirror(mockClient, [], [TaskData('name')])

def test_ChangeTagsOnTaskBeforeStart(client, taskCreator):
	name = 'rtmilk test ChangeTagsOnTaskBeforeStart'
	task = taskCreator.Add(name)
	task.startDate.Set(datetime.today() + timedelta(days=2))
	task.tags.Set({'rtm-test-tag1', 'rtm-test-tag2'})
	task.complete.Set(True)

	tasks = client.Get(f'name: {name}')
	assert len(tasks) == 1
	task = tasks[0]

	taskData = TaskData.FromTask(task)
	taskData.tags -= {'rtm-test-tag1'}
	Mirror(client, [task], [taskData])

	tasks = client.Get(f'name: {name}')
	assert len(tasks) == 1
	assert tasks[0].tags.value == {'rtm-test-tag2'}
