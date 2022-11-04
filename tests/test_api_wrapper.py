from datetime import datetime, timedelta
from logging import info

from dateutil.tz import gettz
from pydantic import ValidationError
from pytest import mark, raises

from rtmilk import AuthResponse, EchoResponse, PriorityDirectionEnum, PriorityEnum, RTMError, TasksGetList
from rtmilk.models import RTMList, RTMSmartList

def test_validation(api, timeline):
	with raises(ValidationError):
		_ = api.TasksAdd(timeline=timeline, name=None)
	taskResponse = api.TasksAdd(timeline=timeline, name=42) # doesn't throw a validation error
	api.TasksDelete(timeline=timeline, list_id=taskResponse.list.id, taskseries_id=taskResponse.list.taskseries[0].id, task_id=taskResponse.list.taskseries[0].task[0].id)

@mark.asyncio
async def test_validation_async(apiAsync, timeline):
	with raises(ValidationError):
		_ = await apiAsync.TasksAdd(timeline=timeline, name=None)
	taskResponse = await apiAsync.TasksAdd(timeline=timeline, name=42) # doesn't throw a validation error
	await apiAsync.TasksDelete(timeline=timeline, list_id=taskResponse.list.id, taskseries_id=taskResponse.list.taskseries[0].id, task_id=taskResponse.list.taskseries[0].task[0].id)

def test_echo(api):
	response = api.TestEcho(a='1', b='2')
	assert isinstance(response, EchoResponse), response

@mark.asyncio
async def test_async_echo(apiAsync):
	response = await apiAsync.TestEcho(a='1', b='2')
	assert isinstance(response, EchoResponse), response

def test_check_token(api):
	response = api.AuthCheckToken(api.secrets.token)
	assert isinstance(response, AuthResponse)

def test_add_and_delete_basic_task(api, timeline):
	task = api.TasksAdd(timeline, 'test_add_and_delete_basic_task')
	api.TasksDelete(
		timeline, task.list.id,
		task.list.taskseries[0].id,
		task.list.taskseries[0].task[0].id)

@mark.asyncio
async def test_async_add_and_delete_basic_task(apiAsync, timeline):
	task = await apiAsync.TasksAdd(timeline, 'test_async_add_and_delete_basic_task')
	await apiAsync.TasksDelete(
		timeline, task.list.id,
		task.list.taskseries[0].id,
		task.list.taskseries[0].task[0].id)

def test_pf_use_case(api, timeline, taskCreator):
	prefix1 = 'prefix1: '
	prefix2 = 'prefix2: '
	suffix1 = 'suffix1'
	suffix2 = 'suffix2'
	_ = taskCreator.Add(prefix1 + suffix1)
	_ = taskCreator.Add(prefix1 + suffix2)
	_ = taskCreator.Add(prefix2 + suffix1)
	task4 = taskCreator.Add(prefix2 + suffix2)
	api.TasksComplete(timeline, task4.list.id, task4.list.taskseries[0].id, task4.list.taskseries[0].task[0].id)

	emptyListResponse = api.TasksGetList(filter=
		f'tag:auto AND tag:computer AND status:incomplete AND (name:"{prefix1}" OR name:"{prefix2}"')
	info(emptyListResponse)

	nonEmptyListResponse = api.TasksGetList(filter=
		f'(name:"{prefix1}" OR name:"{prefix2}"')
	info(nonEmptyListResponse)

def test_add_and_delete_complex_task(api, timeline):
	task = api.TasksAdd(timeline, 'test_add_and_delete_complex_task')

	task = api.TasksAddTags(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, ['tag1'])
	assert {'tag1'} == set(task.list.taskseries[0].tags.tag)

	task = api.TasksSetTags(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, tags=['tag2'])
	assert {'tag2'} == set(task.list.taskseries[0].tags.tag)

	task = api.TasksRemoveTags(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, ['tag2'])
	assert set() == set(task.list.taskseries[0].tags)

	noteResponse = api.TasksNotesAdd(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, 'title', 'body')
	# assert noteResponse.note.title == 'title' # fails, but it's the service itself
	assert noteResponse.note.body == 'title\nbody'

	response = api.TasksSetPriority(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, priority=PriorityEnum.Priority3)
	# assert response.taskseries[0].task[0].priority == PriorityEnum.Priority3 # fails, but it's the service itself

	response = api.TasksMovePriority(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, PriorityDirectionEnum.Up)
	# assert response.list.taskseries[0].task[0].priority == PriorityEnum.Priority2 # fails, but it's the service itself

	response = api.TasksSetName(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, name='test_add_and_delete_complex_task - renamed')
	assert response.list.taskseries[0].name == 'test_add_and_delete_complex_task - renamed'

	response = api.TasksComplete(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id)
	assert response.list.taskseries[0].task[0].completed is not None

	api.TasksDelete(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id)

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

	updatedTask = api.TasksSetDueDate(timeline, listId, taskSeriesId, taskId, due=dueDate)
	assert updatedTask.list.taskseries[0].task[0].due == dueDate

	updatedTask = api.TasksSetStartDate(timeline, listId, taskSeriesId, taskId, start=startDate)
	assert updatedTask.list.taskseries[0].task[0].start == startDate

	api.TasksAddTags(timeline, listId, taskSeriesId, taskId, ['tag1'])

	updatedTask = api.TasksSetDueDate(timeline, listId, taskSeriesId, taskId, due=dueDate2)
	assert updatedTask.list.taskseries[0].task[0].due == dueDate2

	updatedTask = api.TasksSetStartDate(timeline, listId, taskSeriesId, taskId, start=startDate2)
	assert updatedTask.list.taskseries[0].task[0].start == startDate2

def test_get_list(api, task): # pylint: disable=unused-argument
	allTasks = api.TasksGetList()
	if allTasks.tasks.list is None:
		return
	info([x.id for x in allTasks.tasks.list])
	for list_ in allTasks.tasks.list:
		info(f'List ID: {list_.id}')

def test_last_sync(api, taskCreator):
	start = datetime.utcnow()
	noChange = api.TasksGetList(last_sync=start)
	assert noChange.tasks.list is None, 'No tasks added at the start'
	task1 = taskCreator.Add('task 1')
	task1CreateTime = task1.list.taskseries[0].created

	# last_sync is inclusive
	exactTimeQuery = api.TasksGetList(last_sync=task1CreateTime)
	assert exactTimeQuery.tasks.list is not None
	assert exactTimeQuery.tasks.list[0].taskseries is not None
	assert len(exactTimeQuery.tasks.list[0].taskseries) == 1, f'One task added: {exactTimeQuery.tasks}'

	oneAdded = api.TasksGetList(last_sync=start)
	assert oneAdded.tasks.list is not None
	assert oneAdded.tasks.list[0].taskseries is not None
	assert len(oneAdded.tasks.list[0].taskseries) == 1, f'One task added: {oneAdded.tasks}'

	noChange = api.TasksGetList(last_sync=task1CreateTime + timedelta(seconds=1))
	assert noChange.tasks.list is None, f'No tasks added after: {noChange.tasks}'

def test_lists_get_list(api):
	allLists = api.ListsGetList()
	listNames = [x.name for x in allLists.lists.list]
	assert 'Inbox' in listNames, listNames
	assert 'Sent' in listNames, listNames
	assert 'Personal' in listNames, listNames
	assert 'Work' in listNames, listNames

def test_add_list(api, timeline):
	list_ = api.ListsAdd(timeline, 'new list')
	assert isinstance(list_.list, RTMList) and not isinstance(list_.list, RTMSmartList)
	assert list_.list.archived is False, list_
	list_ = api.ListsSetName(timeline, list_.list.id, 'new list renamed')
	assert list_.list.name == 'new list renamed', list_
	list_ = api.ListsArchive(timeline, list_.list.id)
	assert list_.list.archived is True, list_
	list_ = api.ListsUnarchive(timeline, list_.list.id)
	assert list_.list.archived is False, list_
	list_ = api.ListsDelete(timeline, list_.list.id)
	assert list_.list.deleted is True, list_

def test_add_smart_list(api, timeline):
	list_ = api.ListsAdd(timeline, 'new smart list', filter='tag:tag1')
	assert isinstance(list_.list, RTMSmartList)
	assert list_.list.archived is False, list_

	# Can do this on the website but API *does* fail
	try:
		list_ = api.ListsSetName(timeline, list_.list.id, 'new smart list renamed')
		assert False, 'Should have failed to change the name on a smart list'
	except RTMError:
		pass

	# Looks like you can't archive a smart list
	try:
		list_ = api.ListsArchive(timeline, list_.list.id)
		assert False, 'Should have failed to archive a smart list'
	except RTMError:
		pass

	list_ = api.ListsDelete(timeline, list_.list.id)
	assert list_.list.deleted is True, list_

def test_subscriptions(api, timeline):
	api.PushGetSubscriptions()
	topics = api.PushGetTopics()
	info(topics)
	try:
		api.PushSubscribe(timeline=timeline, url='http://hook.example', topics='task_created', filter='', push_format='json', lease_seconds='60')
	except RTMError:
		pass

def test_url():
	fake = {'stat': 'ok',
			'tasks': {
				'list': [
					{'id': '123456',
					'taskseries': [
						{'created': '2022-09-28T01:52:58Z',
						'id': '123456',
						'location_id': '',
						'modified': '2022-09-28T01:52:58Z',
						'name': 'Test',
						'notes': [],
						'parent_task_id': '',
						'participants': [],
						'rrule': {'$t': 'FREQ=MONTHLY;INTERVAL=1;WKST=SU',
									'every': '0'},
						'source': 'js',
						'tags': [],
						'task': [
							{'added': '2022-09-28T01:52:58Z',
							'completed': '',
							'deleted': '',
							'due': '2022-10-27T15:00:00Z',
							'estimate': '',
							'has_due_time': '0',
							'has_start_time': '0',
							'id': '123456',
							'postponed': '0',
							'priority': 'N',
							'start': ''}
							],
						'url': '7:a'},
						]}],
			'rev': '87847jglkfujagg7gei543897jgslkg'}}

	r = TasksGetList.Out(**fake)
	print(r)
