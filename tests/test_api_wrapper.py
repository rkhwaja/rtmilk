from datetime import datetime, timedelta, UTC
from logging import info
from random import randint
from uuid import uuid4

from dateutil.tz import gettz
from pydantic import ValidationError
from pytest import mark, raises

from rtmilk import AuthResponse, EchoResponse, FailStat, NotePayload, PriorityDirectionEnum, PriorityEnum, RTMList, RTMSmartList, Tags, TaskResponse, TaskSeries
from rtmilk._sansio import TasksGetList

def test_validation(api, timeline):
	with raises(ValidationError):
		_ = api.TasksAdd(timeline=timeline, name=None)
	with raises(ValidationError):
		_ = api.TasksAdd(timeline=timeline, name=randint(0, 10000)) # pydantic 2 doesn't coerce a number to a string

@mark.asyncio
async def test_validation_async(apiAsync, timeline):
	with raises(ValidationError):
		_ = await apiAsync.TasksAdd(timeline=timeline, name=None)
	with raises(ValidationError):
		_ = await apiAsync.TasksAdd(timeline=timeline, name=randint(0, 10000)) # pydantic 2 doesn't coerce a number to a string

def test_echo(api):
	response = api.TestEcho(a='1', b='2')
	assert isinstance(response, EchoResponse), response

@mark.asyncio
async def test_async_echo(apiAsync):
	response = await apiAsync.TestEcho(a='1', b='2')
	assert isinstance(response, EchoResponse), response

def test_that_unions_are_necessary_for_tag_list(api, timeline, task):
	taskList = api.TasksGetList(filter=f'name:"{task.list.taskseries[0].name}"')
	theTaskSeries = taskList.tasks.list[0].taskseries[0]

	assert isinstance(theTaskSeries, TaskSeries)
	assert isinstance(theTaskSeries.tags, list)
	assert len(theTaskSeries.tags) == 0

	response = api.TasksSetTags(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, ['rtmilk-test-tag1'])
	assert isinstance(response, TaskResponse)
	assert isinstance(response.list.taskseries[0].tags, Tags)
	assert isinstance(response.list.taskseries[0].tags.tag, list)
	assert len(response.list.taskseries[0].tags.tag) == 1

	taskList = api.TasksGetList(filter=f'name:"{task.list.taskseries[0].name}"')
	theTaskSeries = taskList.tasks.list[0].taskseries[0]
	assert isinstance(theTaskSeries.tags, Tags)
	assert isinstance(theTaskSeries.tags.tag, list)
	assert len(theTaskSeries.tags.tag) == 1

def test_that_unions_are_necessary_for_notes_list(api, timeline, task):
	assert isinstance(task, TaskResponse)
	assert isinstance(task.list.taskseries[0].notes, list)
	assert len(task.list.taskseries[0].notes) == 0

	taskList = api.TasksGetList(filter=f'name:"{task.list.taskseries[0].name}"')
	theTaskSeries = taskList.tasks.list[0].taskseries[0]
	assert isinstance(theTaskSeries, TaskSeries)
	assert isinstance(theTaskSeries.notes, list)
	assert len(theTaskSeries.notes) == 0

	# add a note
	_ = api.TasksNotesAdd(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, 'note title', 'note body')

	# reget the task
	taskList = api.TasksGetList(filter=f'name:"{task.list.taskseries[0].name}"')
	theTaskSeries = taskList.tasks.list[0].taskseries[0]
	assert isinstance(theTaskSeries, TaskSeries)

	assert isinstance(theTaskSeries.notes, NotePayload)
	assert isinstance(theTaskSeries.notes.note, list)
	assert len(theTaskSeries.notes.note) == 1

def test_optional_in_task_list_payload(api, newList):
	# this call returns an object with "list" in TaskListPayload, but no taskseries in TasksInListPayload
	noTasks = api.TasksGetList(list_id=newList.list.id)
	assert hasattr(noTasks.tasks, 'list') is True
	assert hasattr(noTasks.tasks.list, 'taskseries') is False

	# this call returns an object missing "list" from TaskListPayload
	noTasks = api.TasksGetList(filter=f'name:"{uuid4()}"')
	assert hasattr(noTasks.tasks, 'list') is True
	assert hasattr(noTasks.tasks.list, 'taskseries') is False

def test_check_token(api):
	response = api.AuthCheckToken(api.secrets.token)
	assert isinstance(response, AuthResponse)

def test_add_and_delete_basic_task(api, timeline):
	task = api.TasksAdd(timeline, f'test_add_and_delete_basic_task {uuid4()}')
	api.TasksDelete(
		timeline, task.list.id,
		task.list.taskseries[0].id,
		task.list.taskseries[0].task[0].id)

@mark.asyncio
async def test_async_add_and_delete_basic_task(apiAsync, timeline):
	task = await apiAsync.TasksAdd(timeline, f'test_async_add_and_delete_basic_task {uuid4()}')
	await apiAsync.TasksDelete(
		timeline, task.list.id,
		task.list.taskseries[0].id,
		task.list.taskseries[0].task[0].id)

def test_pf_use_case(api, timeline, taskCreatorAPI):
	prefix1 = 'prefix1: '
	prefix2 = 'prefix2: '
	suffix1 = 'suffix1'
	suffix2 = 'suffix2'
	_ = taskCreatorAPI.Add(prefix1 + suffix1 + str(uuid4()))
	_ = taskCreatorAPI.Add(prefix1 + suffix2 + str(uuid4()))
	_ = taskCreatorAPI.Add(prefix2 + suffix1 + str(uuid4()))
	task4 = taskCreatorAPI.Add(prefix2 + suffix2)
	api.TasksComplete(timeline, task4.list.id, task4.list.taskseries[0].id, task4.list.taskseries[0].task[0].id)

	emptyListResponse = api.TasksGetList(filter=
		f'tag:auto AND tag:computer AND status:incomplete AND (name:"{prefix1}" OR name:"{prefix2}"')
	info(emptyListResponse)

	nonEmptyListResponse = api.TasksGetList(filter=
		f'(name:"{prefix1}" OR name:"{prefix2}"')
	info(nonEmptyListResponse)

def test_add_and_delete_complex_task(api, timeline):
	name = f'test_add_and_delete_complex_task {uuid4()}'
	task = api.TasksAdd(timeline, name)

	tag1 = 'rtmilk-test-tag1'
	task = api.TasksAddTags(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, [tag1])
	assert {tag1} == set(task.list.taskseries[0].tags.tag)

	tag2 = 'rtmilk-test-tag2'
	task = api.TasksSetTags(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, tags=[tag2])
	assert {tag2} == set(task.list.taskseries[0].tags.tag)

	task = api.TasksRemoveTags(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, [tag2])
	assert set() == set(task.list.taskseries[0].tags)

	noteResponse = api.TasksNotesAdd(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, 'title', 'body')
	# assert noteResponse.note.title == 'title' # fails, but it's the service itself
	assert noteResponse.note.body == 'title\nbody'

	response = api.TasksSetPriority(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, priority=PriorityEnum.Priority3)
	# assert response.taskseries[0].task[0].priority == PriorityEnum.Priority3 # fails, but it's the service itself

	response = api.TasksMovePriority(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, PriorityDirectionEnum.Up)
	# assert response.list.taskseries[0].task[0].priority == PriorityEnum.Priority2 # fails, but it's the service itself

	response = api.TasksSetName(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id, name=name + ' renamed')
	assert response.list.taskseries[0].name == name + ' renamed'

	response = api.TasksComplete(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id)
	assert response.list.taskseries[0].task[0].completed is not None

	api.TasksDelete(timeline, task.list.id, task.list.taskseries[0].id, task.list.taskseries[0].task[0].id)

def test_delete_non_existing_task(api, timeline):
	result = api.TasksDelete(timeline, '42', '43', '')
	assert isinstance(result, FailStat)

def test_tags(api, timeline, task):
	listId = task.list.id
	taskSeriesId = task.list.taskseries[0].id
	taskId = task.list.taskseries[0].task[0].id

	api.TasksAddTags(timeline, listId, taskSeriesId, taskId, ['rtmilk-test-tag1'])
	assert 'rtmilk-test-tag1' in {x.name for x in api.TagsGetList().tags.tag}

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

	api.TasksAddTags(timeline, listId, taskSeriesId, taskId, ['rtmilk-test-tag1'])

	updatedTask = api.TasksSetDueDate(timeline, listId, taskSeriesId, taskId, due=dueDate2)
	assert updatedTask.list.taskseries[0].task[0].due == dueDate2

	updatedTask = api.TasksSetStartDate(timeline, listId, taskSeriesId, taskId, start=startDate2)
	assert updatedTask.list.taskseries[0].task[0].start == startDate2

def test_set_wrong_start_due_dates(api, timeline, task):
	listId = task.list.id
	taskSeriesId = task.list.taskseries[0].id
	taskId = task.list.taskseries[0].task[0].id

	settings = api.SettingsGetList()
	userTimezone = gettz(settings.settings.timezone)

	dueDate = datetime(2021, 6, 1, 0, 0, 0, tzinfo=userTimezone)
	startDate = datetime(2021, 7, 1, 0, 0, 0, tzinfo=userTimezone)

	updatedTask = api.TasksSetDueDate(timeline, listId, taskSeriesId, taskId, due=dueDate)
	assert updatedTask.list.taskseries[0].task[0].due == dueDate

	updatedTask = api.TasksSetStartDate(timeline, listId, taskSeriesId, taskId, start=startDate)
	assert isinstance(updatedTask, FailStat)

def test_get_list(api, task): # noqa: ARG001
	allTasks = api.TasksGetList()
	if allTasks.tasks.list is None:
		return
	info([x.id for x in allTasks.tasks.list])
	for list_ in allTasks.tasks.list:
		info(f'List ID: {list_.id}')

def test_last_sync(api, taskCreatorAPI):
	start = datetime.now(UTC)
	noChange = api.TasksGetList(last_sync=start)
	assert noChange.tasks.list is None, 'No tasks added at the start'
	task1 = taskCreatorAPI.Add(f'task 1 {uuid4()}')
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

def test_add_list(api, timeline, newList):
	assert isinstance(newList.list, RTMList)
	assert not isinstance(newList.list, RTMSmartList)
	assert newList.list.archived is False, newList
	list_ = api.ListsSetName(timeline, newList.list.id, newList.list.name +' renamed')
	assert list_.list.name == newList.list.name + ' renamed', list_
	list_ = api.ListsArchive(timeline, list_.list.id)
	assert list_.list.archived is True, list_
	list_ = api.ListsUnarchive(timeline, list_.list.id)
	assert list_.list.archived is False, list_

def test_add_smart_list(api, timeline, newSmartList):
	assert isinstance(newSmartList.list, RTMSmartList)
	assert newSmartList.list.archived is False, newSmartList

	# Can do this on the website but API *does* fail
	result = api.ListsSetName(timeline, newSmartList.list.id, newSmartList.list.name + ' renamed')
	assert isinstance(result, FailStat), 'Should have failed to change the name on a smart list'

	# Looks like you can't archive a smart list
	result = api.ListsArchive(timeline, newSmartList.list.id)
	assert isinstance(result, FailStat), 'Should have failed to archive a smart list'

def test_subscriptions(api, timeline):
	api.PushGetSubscriptions()
	topics = api.PushGetTopics()
	info(topics)
	api.PushSubscribe(timeline=timeline, url='https://hook.example', topics='task_created', filter='', push_format='json', lease_seconds='60')

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
							'start': ''},
							],
						'url': '7:a'},
						]}],
			'rev': '87847jglkfujagg7gei543897jgslkg'}}

	r = TasksGetList.Out(**fake)
	print(r)
