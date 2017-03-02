class Renderer(object):
	"""
	The renderer superclass that allows for modular rendering programs

	__init__(self, app, options)
	loop(self)

	Renderer._app
	Renderer._options
	"""

	def __init__(self, app, options):
		"""Initialize the basic necessities of a Renderer"""

		# Initialize variables
		self._app = app
		self._options = options

	def loop(self):
		"""Loop. This is a placeholder to tell you that this needs to be implemented"""

		pass
