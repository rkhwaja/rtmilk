from .api import _ApiSig

_AUTHORIZATION_URL = 'https://www.rememberthemilk.com/services/auth/'

class AuthorizationSession:
	def __init__(self, api, perms):
		self._api = api
		self._frob = api.AuthGetFrob()
		params = {'api_key': self._api.apiKey, 'perms': perms, 'frob': self._frob}
		params['api_sig'] = _ApiSig(self._api.sharedSecret, params)
		self.url = _AUTHORIZATION_URL + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])

	def Done(self):
		token = self._api.AuthGetToken(self._frob)
		self._api.SetToken(token)
		return token
