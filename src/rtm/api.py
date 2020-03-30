from hashlib import md5
from logging import getLogger

from requests import get

_restUrl = 'https://api.rememberthemilk.com/services/rest/'
_log = getLogger('rtm')

class RTMError(Exception):
	def __init__(self, code, message):
		super().__init__(self)
		self.code = code
		self.message = message

	def __repr__(self):
		return f'<RTMError code={self.code}, message={self.message}>'

def _ApiSig(sharedSecret, params):
	sortedItems = sorted(params.items(), key=lambda x: x[0])
	# _log.info(f'sortedItems={sortedItems}')
	concatenatedParams = ''.join((key + value for key, value in sortedItems))
	return md5((sharedSecret + concatenatedParams).encode()).hexdigest()

class API:
	"""
	Low-level API wrapper
	parameter names are the same as on the service itself
	Wraps failures in exceptions
	Checks validity of parameters to the extent possible
	Returns the dictionary with the common parts removed (e.g. 'stat')
	"""
	def __init__(self, apiKey, sharedSecret, storage):
		self.apiKey = apiKey
		self.sharedSecret = sharedSecret
		self.storage = storage

	def SetToken(self, token):
		self.storage.Save(token)

	def _ApiSig(self, params):
		return _ApiSig(self.sharedSecret, params)

	def _MethodParams(self, methodName):
		return {'method': methodName, 'api_key': self.apiKey, 'format': 'json', 'v': '2'}

	def _CallUnauthorized(self, method, **params):
		_log.info(f'_CallUnauthorized: {method}, {params}')
		params.update(self._MethodParams(method))
		params['api_sig'] = self._ApiSig(params)
		rsp = get(_restUrl, params=params).json()['rsp']
		stat = rsp['stat']
		if stat == 'ok':
			del rsp['stat']
			return rsp
		assert stat == 'fail', rsp
		err = rsp['err']
		raise RTMError(int(err['code']), err['msg'])

	def _CallAuthorized(self, method, **params):
		_log.info(f'_CallAuthorized: {method}, {params}')
		params.update(self._MethodParams(method))
		params.update({'auth_token': self.storage.Load()})
		params['api_sig'] = self._ApiSig(params)
		rsp = get(_restUrl, params=params).json()['rsp']
		stat = rsp['stat']
		if stat == 'ok':
			del rsp['stat']
			# _log.info(f'_CallAuthorized -> {rsp}')
			return rsp
		assert stat == 'fail', rsp
		err = rsp['err']
		raise RTMError(int(err['code']), err['msg'])

	def TestEcho(self, **params):
		_log.info(f'Echo: {params}')
		rsp = self._CallUnauthorized('rtm.test.echo', **params)
		assert rsp['method'] == 'rtm.test.echo', rsp
		del rsp['method']
		assert rsp['api_key'] == self.apiKey, rsp
		del rsp['api_key']
		assert rsp['format'] == 'json', rsp
		del rsp['format']
		assert rsp['v'] == '2', rsp
		del rsp['v']
		del rsp['api_sig']
		return rsp

	def AuthGetFrob(self):
		rsp = self._CallUnauthorized('rtm.auth.getFrob')
		return rsp['frob']

	def AuthGetToken(self, frob):
		rsp = self._CallUnauthorized('rtm.auth.getToken', frob=frob)
		return rsp['auth']['token']

	def AuthCheckToken(self):
		return self._CallAuthorized('rtm.auth.checkToken')

	def PushGetSubscriptions(self):
		return self._CallAuthorized('rtm.push.getSubscriptions')['subscriptions']

	def PushGetTopics(self):
		return self._CallAuthorized('rtm.push.getTopics')['topics']

	def PushSubscribe(self, url, topics, push_format, timeline, **args):
		# optional args are lease_seconds and filter
		return self._CallAuthorized('rtm.push.subscribe', url=url, topics=topics, push_format=push_format, timeline=timeline, **args)

	def PushUnsubscribe(self, timeline, subscription_id):
		self._CallAuthorized('rtm.push.unsubscribe', timeline=timeline, subscription_id=subscription_id)

	def TimelinesCreate(self):
		rsp = self._CallAuthorized('rtm.timelines.create')
		return rsp['timeline']

	def SettingsGetList(self):
		rsp = self._CallAuthorized('rtm.settings.getList')
		return rsp['settings']

	def TagsGetList(self):
		return self._CallAuthorized('rtm.tags.getList')['tags']['tag']

	def TasksAdd(self, timeline, name, **args):
		# optional args are list_id, parse (1 or not), parent_task_id, external_id
		rsp = self._CallAuthorized('rtm.tasks.add', timeline=timeline, name=name, **args)
		return rsp

	def TasksAddTags(self, timeline, list_id, taskseries_id, task_id, tags):
		rsp = self._CallAuthorized('rtm.tasks.addTags', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)
		return rsp

	def TasksComplete(self, timeline, list_id, taskseries_id, task_id):
		rsp = self._CallAuthorized('rtm.tasks.complete', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)
		return rsp

	def TasksDelete(self, timeline, list_id, taskseries_id, task_id):
		rsp = self._CallAuthorized('rtm.tasks.delete', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id)
		return rsp

	def TasksGetList(self, **args):
		# optional args are list_id, filter, last_sync
		rsp = self._CallAuthorized('rtm.tasks.getList', **args)
		return rsp['tasks']

	def TasksMovePriority(self, timeline, list_id, taskseries_id, task_id, direction):
		rsp = self._CallAuthorized('rtm.tasks.movePriority', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, direction=direction)
		return rsp

	def TasksRemoveTags(self, timeline, list_id, taskseries_id, task_id, tags):
		rsp = self._CallAuthorized('rtm.tasks.removeTags', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, tags=tags)
		return rsp

	def TasksSetDueDate(self, timeline, list_id, taskseries_id, task_id, **args):
		# optional args are due, has_due_time, parse
		rsp = self._CallAuthorized('rtm.tasks.setDueDate', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **args)
		return rsp

	def TasksSetName(self, timeline, list_id, taskseries_id, task_id, name):
		rsp = self._CallAuthorized('rtm.tasks.setName', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, name=name)
		return rsp

	def TasksSetStartDate(self, timeline, list_id, taskseries_id, task_id, **args):
		# optional args are start, has_start_time, parse
		rsp = self._CallAuthorized('rtm.tasks.setStartDate', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **args)
		return rsp

	def TasksSetTags(self, timeline, list_id, taskseries_id, task_id, **args):
		# optional args are tags
		rsp = self._CallAuthorized('rtm.tasks.setTags', timeline=timeline, list_id=list_id, taskseries_id=taskseries_id, task_id=task_id, **args)
		return rsp
