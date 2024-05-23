from .api_sync import UnauthorizedAPI
from .models import _RaiseIfError
from ._sansio import ApiSig

_AUTHORIZATION_URL = 'https://www.rememberthemilk.com/services/auth/'

class AuthorizationSession:
	"""Helper for authorizing an app against the RTM API"""

	def __init__(self, apiKey, sharedSecret, perms):
		self._api = UnauthorizedAPI(apiKey, sharedSecret)
		self._frob = _RaiseIfError(self._api.AuthGetFrob())
		params = {'api_key': apiKey, 'perms': perms, 'frob': self._frob}
		params['api_sig'] = ApiSig(sharedSecret, params)
		self.url = _AUTHORIZATION_URL + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])

	def Done(self):
		return _RaiseIfError(self._api.AuthGetToken(self._frob))
