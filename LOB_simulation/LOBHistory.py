

class LOBHistory(object):
	"""docstring for orderBookHistory."""
	def __init__(self, env, o_book, name):
		self.order_book = o_book
		self.env = env
		# self.order_book = o_book
		self.name = name

	def log(self):
		while True:
			time = 10

			yield self.env.timeout(time)
			print('%s Logging %f,' % (self.name, self.env.now))
