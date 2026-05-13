class CheckoutSessionState:
	SESSION_KEY = "checkout_flow"

	def __init__(self, request):
		self.request = request

	def data(self):
		return self.request.session.get(self.SESSION_KEY, {})

	def get(self, key, default=None):
		return self.data().get(key, default)

	def update(self, new_values):
		data = self.data()
		data.update(new_values)
		self.request.session[self.SESSION_KEY] = data
		self.request.session.modified = True

	def clear(self):
		if self.SESSION_KEY in self.request.session:
			del self.request.session[self.SESSION_KEY]
			self.request.session.modified = True
