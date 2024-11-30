from __future__ import annotations

from typing import Annotated, TypeVar

from pydantic import BeforeValidator
from pydantic.networks import HttpUrl, UrlConstraints

def EmptyStringToNone(value):
	if value == '':
		return None
	return value

WrappedType = TypeVar('WrappedType')

EmptyStrToNone = Annotated[
	WrappedType,
	BeforeValidator(EmptyStringToNone)
]

HttpsUrl = Annotated[
    HttpUrl, UrlConstraints(allowed_schemes=['https'])
]
