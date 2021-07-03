from logging import getLogger
from typing import Any, Optional

from pydantic import BaseModel, PrivateAttr # pylint: disable=no-name-in-module

_log = getLogger('rtm')

class List(BaseModel):
	_client = PrivateAttr(None)
	id: str
	_name: str = PrivateAttr()
	deleted: bool
	locked: bool
	archived: bool
	position: int
	smart: bool
	filter: Optional[str]

	def __init__(self, **data: Any):
		super().__init__(**data)
		self._name: str = data['name']
		self._client = data['client']

	@property
	def name(self) -> str:
		return self._name

	def _SetName(self, value):
		_log.info(f'Setting name to {value}')
		assert isinstance(value, str)
		self._name = value
		self._client.api.ListsSetName(self._client.timeline, self.id, self._name)

	def __setattr__(self, key, value):
		if key == 'name':
			self._SetName(value)
			return
		super().__setattr__(key, value)
