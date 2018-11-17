# Andrew Bogdan
# app.py
"""
	The thing that interacts with the OS and what's imported by __main__ through __init__.
"""

# Imports
import copy
import curses
import json
import os
import traceback

from mirec_miskuf_json import json_loads_str

from renderer import Renderer
from game import Game

# Classes
class App(object):
	"""
	The all-encompassing class which connects the computer, game, and the renderer

	App.__init__(self)
	App._loop(self)
	App._quit(self)
	App.stop(self)
	App.start(self)

	App._game
	App._is_running
	App._options
	App._renderer
	App._screen
	"""

	def __init__(self):
		"""Intialize App, starting the game."""

		# Load game options
		game_options_path = os.path.join(	os.path.dirname(__file__), 
											"options.json")
		game_options_file = open(game_options_path, 'r')
		self._options = json_loads_str(game_options_file.read())
		game_options_file.close()

		# Load renderer options
		renderer_options_path = os.path.join(	os.path.dirname(__file__),
												"renderer",
												"options.json")
		renderer_options_file = open(renderer_options_path, 'r')
		renderer_options = json_loads_str(renderer_options_file.read())
		renderer_options_file.close()

		# Initialize variables
		self._is_running = False;

		self._game = Game(self, self._options)
		self._renderer = Renderer(self, renderer_options)

		# Start curses for I/O
		self._screen = curses.initscr()

		curses.noecho()
		curses.cbreak()
		curses.curs_set(0)
		self._screen.nodelay(1)
		self._screen.keypad(1)

	def _loop(self):
		"""Perform a main game loop."""

		# Loop the subclasses
		self._game.loop()
		self._renderer.loop()

		# Get and evaluate I/O
		key = self._screen.getch()

		# Evaluate text input
		if key != curses.ERR:
			try:

				self._game.eval_echo(chr(key))

			except ValueError:

				pass

		# Evaluate the first key binding which does something
		if str(key) in self._options["controls"] and key != curses.ERR:
			for control_string in self._options["controls"][str(key)]:
				# This if clause executes the action and returns a boolean if it did anything
				if self._game.eval_control_string(control_string):

					break

	def _quit(self):
		"""Clean up and shut down the app."""

		# Shut down curses
		self._screen.keypad(0)
		self._screen.nodelay(0)
		curses.curs_set(1)
		curses.nocbreak()
		curses.echo()
		curses.endwin()

	def stop(self):
		"""Stop looping."""

		self._is_running = False

	def start(self):
		"""Start looping; this is called independently and is the last thing to run."""

		# Loop
		self._is_running = True

		while self._is_running:
			try:

				self._loop()

			except:

				self._quit()
				traceback.print_exc()
				return

		# Quit when the loop stops
		self._quit()