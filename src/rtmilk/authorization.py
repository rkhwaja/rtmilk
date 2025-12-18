from hmac import new, compare_digest
from hashlib import sha256

from .api_sync import UnauthorizedAPI
from .models import _RaiseIfError
from ._sansio import ApiSig

_AUTHORIZATION_URL = 'https://www.rememberthemilk.com/services/auth/'

class AuthorizationSession:
	"""Helper for authorizing an app against the RTM API"""

	def __init__(self, apiKey: str, sharedSecret: str, perms: str):
		self._api = UnauthorizedAPI(apiKey, sharedSecret)
		self._frob = _RaiseIfError(self._api.AuthGetFrob())
		params = {'api_key': apiKey, 'perms': perms, 'frob': self._frob}
		params['api_sig'] = ApiSig(sharedSecret, params)
		self.url = _AUTHORIZATION_URL + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])

	def Done(self):
		return _RaiseIfError(self._api.AuthGetToken(self._frob))

def ValidateWebhookEvent(clientSecret, xHookSignature, eventId):
	timestamp, signature = xHookSignature.split('.')
	expectedSignature = new(clientSecret.encode('utf-8'), timestamp.encode('utf-8') + b'.' + eventId.encode('utf-8'), sha256).hexdigest()
	if compare_digest(expectedSignature, signature) is False:
		raise RuntimeError('Bad signature')
