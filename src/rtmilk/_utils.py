from __future__ import annotations

from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic.fields import ModelField

PydanticField = TypeVar('PydanticField')

# copied from https://github.com/samuelcolvin/pydantic/issues/181
class EmptyStrToNone(Generic[PydanticField]):
	@classmethod
	def __get_validators__(cls):
		yield cls.validate

	@classmethod
	def validate(cls, v: PydanticField, field: ModelField) -> PydanticField | None:
		if v == '':
			return None

		if field.sub_fields[0].type_ == datetime:
			return datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)

		return v
