# Andrew Bogdan
# Feasible Game 3
# Version 0.1

# Imports
import curses
from console_renderer import Renderer

# Classes

class App:
	"""
	The all-encompassing class which connects the computer, game, and the renderer.

	App.__init__(self)
	App._loop(self)
	App.start(self)

	App._game
	App._is_running
	App._renderer
	"""

	def __init__(self):
		"""Intialize App, starting the game."""

		# Initialize variables
		self._is_running = False;

		self._game = Game()
		self._renderer = Renderer(self._game)

		# Start curses for I/O
		self._screen = curses.initscr()

		curses.noecho()
		curses.cbreak()
		self._screen.keypad(1)

	def _loop(self):
		"""Perform a main game loop."""

		self._game.loop()
		self._renderer.loop()

		character = curses.halfdelay(1)

		print character

	def start(self):
		"""Start looping."""

		# Loop
		self._is_running = True

		while self._is_running:

			self._loop()

		# Shut down curses
		self._screen = keypad(0)
		curses.nocbreak()
		curses.echo()
		curses.endwin()

class Game:
	"""
	The class which controls the game, doing modifications on the game state.

	Game.__init__(self)
	Game.loop(self)
	"""

	def __init__(self):
		"""Initialize Game, starting the game."""

		pass

	def loop(self):
		"""Perform a main game loop."""

		pass

# Main

app = App()
app.start()
