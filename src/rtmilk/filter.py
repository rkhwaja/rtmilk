from dataclasses import dataclass
from enum import Enum

from .model import PriorityEnum

# https://www.rememberthemilk.com/help/?ctx=basics.search.advanced

@dataclass
class ListIs:
    name: str

@dataclass
class ListContains:
    substr: str

@dataclass
class Priority:
    value: PriorityEnum

@dataclass
class StatusComplete:
    complete: bool

@dataclass
class TagIs:
    name: str

@dataclass
class TagContains:
    substr: str

@dataclass
class IsTagged:
    value: bool

@dataclass
class LocationIs:
    name: str

@dataclass
class LocatedWithin:
    location: str

@dataclass
class IsLocated:
    value: bool

@dataclass
class IsRepeating:
    value: bool

@dataclass
class NameIs:
    name: str

@dataclass
class NoteContains:
    substr: str

@dataclass
class HasNotes:
    value: bool

@dataclass
class FilenameContains:
    substr: str

@dataclass
class HasAttachments:
    value: bool
