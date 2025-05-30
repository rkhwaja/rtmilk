from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime

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
	@abstractmethod
	def Text(self) -> str:
		pass

@dataclass
class ListIs(ConditionABC):
	name: str

	def Text(self):
		return f'list:"{self.name}"'

@dataclass
class ListContains(ConditionABC):
	substr: str

	def Text(self):
		return f'listContains:"{self.substr}"'

@dataclass
class Priority(ConditionABC):
	value: PriorityEnum

	def Text(self):
		text = {
			PriorityEnum.NoPriority: 'none',
			PriorityEnum.Priority1: '1',
			PriorityEnum.Priority2: '2',
			PriorityEnum.Priority3: '3',
		}[self.value]
		return f'priority:{text}'

@dataclass
class Status(ConditionABC):
	complete: bool

	def Text(self):
		return 'status:' + ('completed' if self.complete else 'incomplete')

@dataclass
class TagIs(ConditionABC):
	name: str

	def Text(self):
		return f'tag:{self.name}'

@dataclass
class TagContains(ConditionABC):
	substr: str

	def Text(self):
		return f'tagContains:{self.substr}'

@dataclass
class IsTagged(ConditionABC):
	value: bool

	def Text(self):
		return f'isTagged:{_BoolText(self.value)}'

@dataclass
class LocationIs(ConditionABC):
	name: str

	def Text(self):
		return f'location:{self.name}'

@dataclass
class LocationContains(ConditionABC):
	location: str

	def Text(self):
		return f'locationContains:"{self.location}"'

@dataclass
class LocatedWithin(ConditionABC):
	location: str

	def Text(self):
		return f'locatedWithin:"{self.location}"'

@dataclass
class IsLocated(ConditionABC):
	value: bool

	def Text(self):
		return f'isLocated:{_BoolText(self.value)}'

@dataclass
class IsRepeating(ConditionABC):
	value: bool

	def Text(self):
		return f'isRepeating:{_BoolText(self.value)}'

@dataclass
class NameIs(ConditionABC):
	name: str

	def Text(self):
		return f'name:"{self.name}"'

@dataclass
class NoteContains(ConditionABC):
	substr: str

	def Text(self):
		return f'noteContains:"{self.substr}"'

@dataclass
class HasNotes(ConditionABC):
	value: bool

	def Text(self):
		return f'hasNotes:"{_BoolText(self.value)}"'

@dataclass
class FilenameContains(ConditionABC):
	substr: str

	def Text(self):
		return f'filename:"{self.substr}"'

@dataclass
class HasAttachments(ConditionABC):
	value: bool

	def Text(self):
		return f'hasAttachments:{_BoolText(self.value)}'

@dataclass
class Due(ConditionABC):
	value: str | date

	def Text(self):
		return f'due:{_DateText(self.value)}'

@dataclass
class DueBefore(ConditionABC):
	value: str | date

	def Text(self):
		return f'dueBefore:{_DateText(self.value)}'

@dataclass
class DueAfter(ConditionABC):
	value: str | date

	def Text(self):
		return f'dueAfter:{_DateText(self.value)}'

@dataclass
class DueWithin(ConditionABC):
	value: str

	def Text(self):
		return f'dueWithin:{self.value}'

@dataclass
class Start(ConditionABC):
	value: str | date

	def Text(self):
		return f'start:{_DateText(self.value)}'

@dataclass
class StartBefore(ConditionABC):
	value: str | date

	def Text(self):
		return f'startBefore:{_DateText(self.value)}'

@dataclass
class StartAfter(ConditionABC):
	value: str | date

	def Text(self):
		return f'startAfter:{_DateText(self.value)}'

@dataclass
class StartWithin(ConditionABC):
	value: str

	def Text(self):
		return f'startWithin:{self.value}'

@dataclass
class TimeEstimate(ConditionABC):
	value: str

	def Text(self):
		return f'timeEstimate: "{self.value}"'

@dataclass
class HasTimeEstimate(ConditionABC):
	value: bool

	def Text(self):
		return f'hasTimeEstimate:{_BoolText(self.value)}'

@dataclass
class HasURL(ConditionABC):
	value: bool

	def Text(self):
		return f'hasURL:{_BoolText(self.value)}'

@dataclass
class HasSubtasks(ConditionABC):
	value: bool

	def Text(self):
		return f'hasSubtasks:{_BoolText(self.value)}'

@dataclass
class IsSubtask(ConditionABC):
	value: bool

	def Text(self):
		return f'isSubtask:{_BoolText(self.value)}'

@dataclass
class Completed(ConditionABC):
	value: str | date

	def Text(self):
		return f'completed:{_DateText(self.value)}'

@dataclass
class CompletedBefore(ConditionABC):
	value: str | date

	def Text(self):
		return f'completedBefore:{_DateText(self.value)}'

@dataclass
class CompletedAfter(ConditionABC):
	value: str | date

	def Text(self):
		return f'completedAfter:{_DateText(self.value)}'

@dataclass
class CompletedWithin(ConditionABC):
	value: str

	def Text(self):
		return f'completedWithin:{self.value}'

@dataclass
class Added(ConditionABC):
	value: str | date

	def Text(self):
		return f'added:{_DateText(self.value)}'

@dataclass
class AddedBefore(ConditionABC):
	value: str | date

	def Text(self):
		return f'addedBefore:{_DateText(self.value)}'

@dataclass
class AddedAfter(ConditionABC):
	value: str | date

	def Text(self):
		return f'addedAfter:{_DateText(self.value)}'

@dataclass
class AddedWithin(ConditionABC):
	value: str

	def Text(self):
		return f'addedWithin:{self.value}'

@dataclass
class Updated(ConditionABC):
	value: str | date

	def Text(self):
		return f'updated:{_DateText(self.value)}'

@dataclass
class UpdatedBefore(ConditionABC):
	value: str | date

	def Text(self):
		return f'updatedBefore:{_DateText(self.value)}'

@dataclass
class UpdatedAfter(ConditionABC):
	value: str | date

	def Text(self):
		return f'updatedAfter:{_DateText(self.value)}'

@dataclass
class UpdatedWithin(ConditionABC):
	value: str

	def Text(self):
		return f'updatedWithin:{self.value}'

@dataclass
class Postponed(ConditionABC):
	value: str

	def Text(self):
		return f'postponed:"{self.value}"'

@dataclass
class IsShared(ConditionABC):
	value: bool

	def Text(self):
		return f'isShared:{_BoolText(self.value)}'

@dataclass
class SharedWith(ConditionABC):
	value: str

	def Text(self):
		return f'sharedWith:{self.value}'

@dataclass
class GivenTo(ConditionABC):
	value: str

	def Text(self):
		return f'givenTo:{self.value}'

@dataclass
class GivenBy(ConditionABC):
	value: str

	def Text(self):
		return f'givenBy:{self.value}'

@dataclass
class IsGiven(ConditionABC):
	value: bool

	def Text(self):
		return f'isGiven:{_BoolText(self.value)}'

@dataclass
class Source(ConditionABC):
	value: str

	def Text(self):
		return f'source:{self.value}'

@dataclass
class IncludeArchived(ConditionABC):
	value: bool

	def Text(self):
		return f'includeArchived:{_BoolText(self.value)}'

@dataclass
class And(ConditionABC):
	lhs: ConditionABC
	rhs: ConditionABC

	def Text(self):
		return f'({self.lhs.Text()}) AND ({self.rhs.Text()})'

@dataclass
class Or(ConditionABC):
	lhs: ConditionABC
	rhs: ConditionABC

	def Text(self):
		return f'({self.lhs.Text()}) OR ({self.rhs.Text()})'

@dataclass
class Not(ConditionABC):
	condition: ConditionABC

	def Text(self):
		return f'NOT ({self.condition.Text()})'
