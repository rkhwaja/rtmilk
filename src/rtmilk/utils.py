from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic.fields import ModelField # pylint: disable=no-name-in-module
# from pydantic.main import Model # pylint: disable=no-name-in-module

PydanticField = TypeVar('PydanticField')

# copied from https://github.com/samuelcolvin/pydantic/issues/181
class EmptyStrToNone(Generic[PydanticField]):
	@classmethod
	def __get_validators__(cls):
		yield cls.validate

	@classmethod
	def validate(cls, v: PydanticField, field: ModelField) -> Optional[PydanticField]: # pylint: disable=unsubscriptable-object,unused-argument
		if v == '':
			return None
		return datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)

# class MissingToEmptyList(Generic[PydanticField]):
# 	@classmethod
# 	def __get_validators__(cls):
# 		yield cls.validate

# 	@classmethod
# 	def validate(cls, v: PydanticField, field: ModelField) -> Optional[PydanticField]: #pylint: disable=unused-argument
# 		if v
