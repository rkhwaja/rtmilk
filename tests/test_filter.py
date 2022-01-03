from rtmilk import And, Or, NameIs, Priority, PriorityEnum, Status

def testFilter():
	assert And(NameIs('the-name'), Status(True)).Text() == '(name:"the-name") AND (status:completed)'

	assert Or(Priority(PriorityEnum.Priority1), NameIs('the-name')).Text() == '(priority:1) OR (name:"the-name")'
