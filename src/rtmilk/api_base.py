from .secrets import Secrets, SecretsWithAuthorization

class UnauthorizedAPIBase:
	"""Holds secrets for unauthorized calls"""
	def __init__(self, apiKey, sharedSecret):
		self._secrets = Secrets(apiKey, sharedSecret)

	@property
	def secrets(self):
		return self._secrets

class AuthorizedAPIBase:
	"""Holds secrets for authorized calls"""
	def __init__(self, apiKey, sharedSecret, token):
		self._authSecrets = SecretsWithAuthorization(apiKey, sharedSecret, token)
