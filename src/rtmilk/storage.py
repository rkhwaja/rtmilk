from json import dump, load

class FileStorage:
	def __init__(self, path):
		self.path = path

	def Save(self, token):
		with open(self.path, 'w') as f:
			dump({'token': token}, f)

	def Load(self):
		try:
			with open(self.path) as f:
				return load(f)['token']
		except FileNotFoundError:
			return None
