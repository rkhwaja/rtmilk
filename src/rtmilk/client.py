class Client:
	def __init__(self, api):
		self.api = api
		self.timeline = self.api.TimelinesCreate()
