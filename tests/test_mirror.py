from rtmilk.mirror import Mirror, TaskData

def testMirror(mockClient):
	Mirror(mockClient, [], [TaskData('name')])
