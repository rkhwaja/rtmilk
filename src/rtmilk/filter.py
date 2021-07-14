from abc import ABC
from dataclasses import dataclass
from datetime import date, datetime
from typing import Union

from .models import PriorityEnum

# https://www.rememberthemilk.com/help/?ctx=basics.search.advanced

def _BoolText(value):
	return 'true' if value else 'false'

def _DateText(value):
	if isinstance(value, date):
		# documentation says UK date format (day first) but (my) website says US format
		# each account has a setting which switches between these possibilities
		return datetime.strftime(value, '%m/%d/%Y')
	return f'"{value}"'

class ConditionABC(ABC):
	def Text(self) -> str:
		pass

@dataclass
class ListIs:
	name: str

	def Text(self):
		return f'list:"{self.name}"'

@dataclass
class ListContains:
	substr: str

	def Text(self):
		return f'listContains:"{self.substr}"'

@dataclass
class Priority:
	value: PriorityEnum

	def Text(self):
		text = {
			PriorityEnum.NoPriority: 'none',
			PriorityEnum.Priority1: '1',
			PriorityEnum.Priority2: '2',
			PriorityEnum.Priority3: '3'
		}[self.value]
		return f'priority:{text}'

@dataclass
class Status:
	complete: bool

	def Text(self):
		return 'status:' + ('completed' if self.complete else 'incomplete')

@dataclass
class TagIs:
	name: str

	def Text(self):
		return f'tag:{self.name}'

@dataclass
class TagContains:
	substr: str

	def Text(self):
		return f'tagContains:{self.substr}'

@dataclass
class IsTagged:
	value: bool

	def Text(self):
		return f'isTagged:{_BoolText(self.value)}'

@dataclass
class LocationIs:
	name: str

	def Text(self):
		return f'location:{self.name}'

@dataclass
class LocationContains:
	location: str

	def Text(self):
		return f'locationContains:"{self.location}"'

@dataclass
class LocatedWithin:
	location: str

	def Text(self):
		return f'locatedWithin:"{self.location}"'

@dataclass
class IsLocated:
	value: bool

	def Text(self):
		return f'isLocated:{_BoolText(self.value)}'

@dataclass
class IsRepeating:
	value: bool

	def Text(self):
		return f'isRepeating:{_BoolText(self.value)}'

@dataclass
class NameIs:
	name: str

	def Text(self):
		return f'name:"{self.name}"'

@dataclass
class NoteContains:
	substr: str

	def Text(self):
		return f'noteContains:"{self.substr}"'

@dataclass
class HasNotes:
	value: bool

	def Text(self):
		return f'hasNotes:"{_BoolText(self.value)}"'

@dataclass
class FilenameContains:
	substr: str

	def Text(self):
		return f'filename:"{self.substr}"'

@dataclass
class HasAttachments:
	value: bool

	def Text(self):
		return f'hasAttachments:{_BoolText(self.value)}'

@dataclass
class Due:
	value: Union[str, date]

	def Text(self):
		return f'due:{_DateText(self.value)}'

@dataclass
class DueBefore:
	value: Union[str, date]

	def Text(self):
		return f'dueBefore:{_DateText(self.value)}'

@dataclass
class DueAfter:
	value: Union[str, date]

	def Text(self):
		return f'dueAfter:{_DateText(self.value)}'

@dataclass
class DueWithin:
	value: str

	def Text(self):
		return f'dueWithin:{self.value}'

@dataclass
class Start:
	value: Union[str, date]

	def Text(self):
		return f'start:{_DateText(self.value)}'

@dataclass
class StartBefore:
	value: Union[str, date]

	def Text(self):
		return f'startBefore:{_DateText(self.value)}'

@dataclass
class StartAfter:
	value: Union[str, date]

	def Text(self):
		return f'startAfter:{_DateText(self.value)}'

@dataclass
class StartWithin:
	value: str

	def Text(self):
		return f'startWithin:{self.value}'

@dataclass
class TimeEstimate:
	value: str

	def Text(self):
		return f'timeEstimate: "{self.value}"'

@dataclass
class HasTimeEstimate:
	value: bool

	def Text(self):
		return f'hasTimeEstimate:{_BoolText(self.value)}'

@dataclass
class HasURL:
	value: bool

	def Text(self):
		return f'hasURL:{_BoolText(self.value)}'

@dataclass
class HasSubtasks:
	value: bool

	def Text(self):
		return f'hasSubtasks:{_BoolText(self.value)}'

@dataclass
class IsSubtask:
	value: bool

	def Text(self):
		return f'isSubtask:{_BoolText(self.value)}'

@dataclass
class Completed:
	value: Union[str, date]

	def Text(self):
		return f'completed:{_DateText(self.value)}'

@dataclass
class CompletedBefore:
	value: Union[str, date]

	def Text(self):
		return f'completedBefore:{_DateText(self.value)}'

@dataclass
class CompletedAfter:
	value: Union[str, date]

	def Text(self):
		return f'completedAfter:{_DateText(self.value)}'

@dataclass
class CompletedWithin:
	value: str

	def Text(self):
		return f'completedWithin:{self.value}'

@dataclass
class Added:
	value: Union[str, date]

	def Text(self):
		return f'added:{_DateText(self.value)}'

@dataclass
class AddedBefore:
	value: Union[str, date]

	def Text(self):
		return f'addedBefore:{_DateText(self.value)}'

@dataclass
class AddedAfter:
	value: Union[str, date]

	def Text(self):
		return f'addedAfter:{_DateText(self.value)}'

@dataclass
class AddedWithin:
	value: str

	def Text(self):
		return f'addedWithin:{self.value}'

@dataclass
class Updated:
	value: Union[str, date]

	def Text(self):
		return f'updated:{_DateText(self.value)}'

@dataclass
class UpdatedBefore:
	value: Union[str, date]

	def Text(self):
		return f'updatedBefore:{_DateText(self.value)}'

@dataclass
class UpdatedAfter:
	value: Union[str, date]

	def Text(self):
		return f'updatedAfter:{_DateText(self.value)}'

@dataclass
class UpdatedWithin:
	value: str

	def Text(self):
		return f'updatedWithin:{self.value}'

@dataclass
class Postponed:
	value: str

	def Text(self):
		return f'postponed:"{self.value}"'

@dataclass
class IsShared:
	value: bool

	def Text(self):
		return f'isShared:{_BoolText(self.value)}'

@dataclass
class SharedWith:
	value: str

	def Text(self):
		return f'sharedWith:{self.value}'

@dataclass
class GivenTo:
	value: str

	def Text(self):
		return f'givenTo:{self.value}'

@dataclass
class GivenBy:
	value: str

	def Text(self):
		return f'givenBy:{self.value}'

@dataclass
class IsGiven:
	value: bool

	def Text(self):
		return f'isGiven:{_BoolText(self.value)}'

@dataclass
class Source:
	value: str

	def Text(self):
		return f'source:{self.value}'

@dataclass
class IncludeArchived:
	value: bool

	def Text(self):
		return f'includeArchived:{_BoolText(self.value)}'

@dataclass
class And:
	lhs: ConditionABC
	rhs: ConditionABC

	def Text(self):
		return f'({self.lhs.Text()}) AND ({self.rhs.Text()})'

@dataclass
class Or:
	lhs: ConditionABC
	rhs: ConditionABC

	def Text(self):
		return f'({self.lhs.Text()}) OR ({self.rhs.Text()})'

@dataclass
class Not:
	condition: ConditionABC

	def Text(self):
		return f'NOT ({self.condition.Text()})'
