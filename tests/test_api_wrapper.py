from datetime import datetime, timezone
from logging import info
from pprint import pformat

from dateutil.tz import gettz
from pytest import raises

from rtm import RTMError

# def test_echo(api):
# 	rsp = api.TestEcho(a='1', b='2')
# 	assert rsp.method == 'rtm.test.echo', rsp
# 	assert 'api_key' in rsp.params
# 	assert rsp.params['format'] == 'json', rsp
# 	assert rsp.params['v'] == '2', rsp
# 	assert 'api_sig' in rsp.params, rsp
# 	assert rsp.params['a'] == '1', rsp
# 	assert rsp.params['b'] == '2', rsp

def test_check_token(api):
	api.AuthCheckToken()

def test_add_and_delete_task(api):
	timeline = api.TimelinesCreate()
	task = api.TasksAdd(timeline, 'test_add_and_delete_task')
	info(pformat(task))
	api.TasksDelete(
		timeline, task['list']['id'],
		task['list']['taskseries'][0]['id'],
		task['list']['taskseries'][0]['task'][0]['id'])

def test_delete_non_existing_task(api, timeline):
	with raises(RTMError):
		_ = api.TasksDelete(
			timeline, '42',
			'43', '')

def test_tags(api, timeline, task):
	listId = task['list']['id']
	taskSeriesId = task['list']['taskseries'][0]['id']
	taskId = task['list']['taskseries'][0]['task'][0]['id']

	api.TasksAddTags(timeline, listId, taskSeriesId, taskId, 'tag1')
	assert 'tag1' in {x['name'] for x in api.TagsGetList()}
	allTaskSeries = api.TasksGetList(list_id=listId)['list'][0]['taskseries']
	assert len(allTaskSeries) == 1, allTaskSeries
	assert {'tag1'} == set(allTaskSeries[0]['tags']['tag']), allTaskSeries

	api.TasksAddTags(timeline, listId, taskSeriesId, taskId, 'tag2,tag3')
	assert {'tag1', 'tag2', 'tag3'} <= {x['name'] for x in api.TagsGetList()}
	allTaskSeries = api.TasksGetList(list_id=listId)['list'][0]['taskseries']
	assert len(allTaskSeries) == 1, allTaskSeries
	assert {'tag1', 'tag2', 'tag3'} == set(allTaskSeries[0]['tags']['tag']), allTaskSeries

	api.TasksRemoveTags(timeline, listId, taskSeriesId, taskId, 'tag1,tag3')
	assert {'tag1', 'tag2', 'tag3'} <= {x['name'] for x in api.TagsGetList()}
	allTaskSeries = api.TasksGetList(list_id=listId)['list'][0]['taskseries']
	assert len(allTaskSeries) == 1, allTaskSeries
	assert {'tag2'} == set(allTaskSeries[0]['tags']['tag']), allTaskSeries

	api.TasksSetTags(timeline, listId, taskSeriesId, taskId, tags='tag3')
	allTaskSeries = api.TasksGetList(list_id=listId)['list'][0]['taskseries']
	assert len(allTaskSeries) == 1, allTaskSeries
	assert {'tag3'} == set(allTaskSeries[0]['tags']['tag']), allTaskSeries

def test_dates(api, timeline, task):
	listId = task['list']['id']
	taskSeriesId = task['list']['taskseries'][0]['id']
	taskId = task['list']['taskseries'][0]['task'][0]['id']

	settings = api.SettingsGetList()
	userTimezone = gettz(settings['timezone'])

	dueDate = datetime(2021, 6, 1, 0, 0, 0, tzinfo=userTimezone)

	updatedTask = api.TasksSetDueDate(timeline, listId, taskSeriesId, taskId, due=dueDate.isoformat())
	assert updatedTask['list']['taskseries'][0]['task'][0]['due'] == dueDate.astimezone(timezone.utc).isoformat()[:19] + 'Z'

	startDate = datetime(2021, 5, 1, 0, 0, 0, tzinfo=userTimezone)
	updatedTask = api.TasksSetStartDate(timeline, listId, taskSeriesId, taskId, start=startDate.isoformat())
	assert updatedTask['list']['taskseries'][0]['task'][0]['start'] == startDate.astimezone(timezone.utc).isoformat()[:19] + 'Z'

def test_get_list(api):
	response = api.TasksGetList()
	info([x['id'] for x in response['list']])
	for list_ in response['list']:
		info(f'List: {list_["id"]}')
		if 'taskseries' in list_:
			info(f'taskseries count: {len(list(list_["taskseries"]))}')
		else:
			info(f'task: {list_["id"]}')

def test_lists_get_list(api):
	response = api.ListsGetList()
	info(response)
