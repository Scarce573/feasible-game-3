# Andrew Bogdan
# Console Renderer
# Version 0.1

# Classes

class Renderer:
	"""
	A renderer which uses curses to render onto a console.

	Renderer.__init__(self)
	Renderer.loop(self)

	Renderer._app
	Renderer._options
	"""

	def __init__(self, app, options):
		"""Intialize the Renderer."""

		# Initialize variables
		self._app = app
		self._options = options

	def loop(self):

		pass
