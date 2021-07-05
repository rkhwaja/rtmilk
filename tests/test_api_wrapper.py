from datetime import datetime, timezone
from logging import info

from dateutil.tz import gettz
from pytest import raises

from rtmilk import AuthResponse, EchoResponse, PriorityDirectionEnum, PriorityEnum, RTMError

def test_echo(api):
	response = api.TestEcho(a='1', b='2')
	assert isinstance(response, EchoResponse), response

def test_check_token(api):
	response = api.AuthCheckToken(api.storage.Load())
	assert isinstance(response, AuthResponse)

def test_add_and_delete_basic_task(api):
	timeline = api.TimelinesCreate()
	task = api.TasksAdd(timeline.timeline, 'test_add_and_delete_basic_task')
	api.TasksDelete(
		timeline.timeline, task.list.id,
		task.list.taskseries[0].id,
		task.list.taskseries[0].task[0].id)

def test_add_and_delete_complex_task(api):
	timeline = api.TimelinesCreate()
	task = api.TasksAdd(timeline.timeline, 'test_add_and_delete_complex_task')

	task = api.TasksAddTags(timeline.timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, ['tag1'])
	assert {'tag1'} == set(task.list.taskseries[0].tags.tag)

	task = api.TasksSetTags(timeline.timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, tags=['tag2'])
	assert {'tag2'} == set(task.list.taskseries[0].tags.tag)

	task = api.TasksRemoveTags(timeline.timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, ['tag2'])
	assert set() == set(task.list.taskseries[0].tags)

	noteResponse = api.TasksNotesAdd(timeline.timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, 'title', 'body')
	# assert noteResponse.note.title == 'title' # fails, but it's the service itself
	assert noteResponse.note.body == 'title\nbody'

	response = api.TasksSetPriority(timeline.timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, priority=PriorityEnum.Priority3)
	# assert response.taskseries[0].task[0].priority == PriorityEnum.Priority3 # fails, but it's the service itself

	response = api.TasksMovePriority(timeline.timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, PriorityDirectionEnum.Up)
	# assert response.list.taskseries[0].task[0].priority == PriorityEnum.Priority2 # fails, but it's the service itself

	response = api.TasksSetName(timeline.timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, name='test_add_and_delete_complex_task - renamed')
	assert response.list.taskseries[0].name == 'test_add_and_delete_complex_task - renamed'

	response = api.TasksComplete(timeline.timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id)
	assert response.list.taskseries[0].task[0].completed is not None

	api.TasksDelete(timeline.timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id)

def test_delete_non_existing_task(api, timeline):
	with raises(RTMError):
		_ = api.TasksDelete(
			timeline, '42',
			'43', '')

def test_tags(api, timeline, task):
	listId = task.list.id
	taskSeriesId = task.list.taskseries[0].id
	taskId = task.list.taskseries[0].task[0].id

	api.TasksAddTags(timeline, listId, taskSeriesId, taskId, ['tag1'])
	assert 'tag1' in {x.name for x in api.TagsGetList().tags.tag}
	# allTaskSeries = api.TasksGetList(list_id=listId).tasks.list[0].id
	# api.TasksDelete(
	# 	timeline, task.list.id,
	# 	task.list.taskseries[0].id,
	# 	task.list.taskseries[0].task[0].id)
	# assert len(allTaskSeries) == 1, allTaskSeries
	# assert {'tag1'} == set(allTaskSeries[0]['tags']['tag']), allTaskSeries

	# api.TasksAddTags(timeline, listId, taskSeriesId, taskId, 'tag2,tag3')
	# assert {'tag1', 'tag2', 'tag3'} <= {x['name'] for x in api.TagsGetList()}
	# allTaskSeries = api.TasksGetList(list_id=listId)['list'][0]['taskseries']
	# assert len(allTaskSeries) == 1, allTaskSeries
	# assert {'tag1', 'tag2', 'tag3'} == set(allTaskSeries[0]['tags']['tag']), allTaskSeries

	# api.TasksRemoveTags(timeline, listId, taskSeriesId, taskId, 'tag1,tag3')
	# assert {'tag1', 'tag2', 'tag3'} <= {x['name'] for x in api.TagsGetList()}
	# allTaskSeries = api.TasksGetList(list_id=listId)['list'][0]['taskseries']
	# assert len(allTaskSeries) == 1, allTaskSeries
	# assert {'tag2'} == set(allTaskSeries[0]['tags']['tag']), allTaskSeries

	# api.TasksSetTags(timeline, listId, taskSeriesId, taskId, tags='tag3')
	# allTaskSeries = api.TasksGetList(list_id=listId)['list'][0]['taskseries']
	# assert len(allTaskSeries) == 1, allTaskSeries
	# assert {'tag3'} == set(allTaskSeries[0]['tags']['tag']), allTaskSeries

def test_dates(api, timeline, task):
	listId = task.list.id
	taskSeriesId = task.list.taskseries[0].id
	taskId = task.list.taskseries[0].task[0].id

	settings = api.SettingsGetList()
	userTimezone = gettz(settings.settings.timezone)

	dueDate = datetime(2021, 6, 1, 0, 0, 0, tzinfo=userTimezone)
	dueDate2 = datetime(2021, 6, 2, 0, 0, 0, tzinfo=userTimezone)
	startDate = datetime(2021, 5, 1, 0, 0, 0, tzinfo=userTimezone)
	startDate2 = datetime(2021, 5, 2, 0, 0, 0, tzinfo=userTimezone)

	updatedTask = api.TasksSetDueDate(timeline, listId, taskSeriesId, taskId, due=dueDate.isoformat())
	assert updatedTask.list.taskseries[0].task[0].due == dueDate.astimezone(timezone.utc).isoformat()[:19] + 'Z'

	updatedTask = api.TasksSetStartDate(timeline, listId, taskSeriesId, taskId, start=startDate.isoformat())
	assert updatedTask.list.taskseries[0].task[0].start == startDate.astimezone(timezone.utc).isoformat()[:19] + 'Z'

	api.TasksAddTags(timeline, listId, taskSeriesId, taskId, ['tag1'])

	updatedTask = api.TasksSetDueDate(timeline, listId, taskSeriesId, taskId, due=dueDate2.isoformat())
	assert updatedTask.list.taskseries[0].task[0].due == dueDate2.astimezone(timezone.utc).isoformat()[:19] + 'Z'

	updatedTask = api.TasksSetStartDate(timeline, listId, taskSeriesId, taskId, start=startDate2.isoformat())
	assert updatedTask.list.taskseries[0].task[0].start == startDate2.astimezone(timezone.utc).isoformat()[:19] + 'Z'

def test_get_list(api):
	allTasks = api.TasksGetList()
	if allTasks.tasks.list is None:
		return
	info([x.id for x in allTasks.tasks.list])
	for list_ in allTasks.tasks.list:
		info(f'List ID: {list_.id}')

def test_lists_get_list(api):
	allLists = api.ListsGetList()
	listNames = [x.name for x in allLists.lists.list]
	assert 'Inbox' in listNames, listNames
	assert 'Sent' in listNames, listNames
	assert 'Personal' in listNames, listNames
	assert 'Work' in listNames, listNames
