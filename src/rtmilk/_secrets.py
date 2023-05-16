from dataclasses import dataclass
from hashlib import md5

def _ApiSig(sharedSecret, params):
	sortedItems = sorted(params.items(), key=lambda x: x[0])
	concatenatedParams = ''.join((key + value for key, value in sortedItems))
	return md5((sharedSecret + concatenatedParams).encode()).hexdigest()

@dataclass
class Secrets:
	apiKey: str
	sharedSecret: str

	def _ApiSig(self, params):
		return _ApiSig(self.sharedSecret, params)

	def _MethodParams(self, methodName):
		return {'method': methodName, 'api_key': self.apiKey, 'format': 'json', 'v': '2'}

	def SignParams(self, method, **params):
		params.update(self._MethodParams(method))
		params['api_sig'] = self._ApiSig(params)
		return params

@dataclass
class SecretsWithAuthorization(Secrets):
	token: str

	def SignParams(self, method, **params):
		params.update(self._MethodParams(method))
		params.update({'auth_token': self.token})
		params['api_sig'] = self._ApiSig(params)
		return params
