# Andrew Bogdan
# Console Renderer
# Version 0.1

# Modules
import curses
import os

from mirec_miskuf_json import json_loads_str

from ..renderer_super import Renderer

# Classes

class ConsoleRenderer(Renderer):
	"""
	A renderer which uses curses to render onto a console.

	Renderer.__init__(self)
	Renderer._make_map(self, game_map)
	Renderer._make_message_log(self, game_message_log)
	Renderer.loop(self)

	Renderer._app
	Renderer._chracter_key
	Renderer._options
	"""

	def __init__(self, app, options):
		"""Intialize the Renderer."""

		# Call super.__init__
		super(ConsoleRenderer, self).__init__(app, options)

		# Get id to character dict
		character_key_path = os.path.join(	os.path.dirname(__file__), 
							"character_key.json")
		character_key_file = open(character_key_path, 'r')
		self._character_key = json_loads_str(character_key_file.read())
		character_key_file.close()

	def _make_map(self, game_map):

		# Make a pad for map
		map_pad = curses.newpad(game_map._size[1], game_map._size[0])
		
		# Construct the map pad
		for y_val in range(0, game_map._size[1]):
		    for x_val in range(0, game_map._size[0]):

			tile_to_render = game_map.grid[x_val][y_val]

			perm = min(tile_to_render.layers[-1].keys())
			entity_to_render = tile_to_render.layers[-1][perm]

			ch = self._character_key[entity_to_render.id][0]

			try:

			    map_pad.addch(y_val, x_val, ch)

			except curses.error:

			    pass

		# Return the map pad
		return map_pad

	def _make_message_log(self, game_message_log):

		# Make a pad for message log
		message_log_pad = curses.newpad(4, 48)

		# Construct the message log pad
		try: message_log_pad.addstr(0, 0, game_message_log[-4])
		except: pass

		try: message_log_pad.addstr(1, 0, game_message_log[-3])
		except: pass

		try: message_log_pad.addstr(2, 0, game_message_log[-2])
		except: pass

		try: message_log_pad.addstr(3, 0, game_message_log[-1])
		except: pass

		# Return the message log pad
		return message_log_pad

	def loop(self):

		# Call super.loop, which is unnecessary for now but good form
		super(ConsoleRenderer, self).loop()

		# Load information
		game_map = self._app._game._state.map
		game_message_log = self._app._game._state.message_log

		# Get pads
		map_pad = self._make_map(game_map)
		message_log_pad = self._make_message_log(game_message_log)

		# Print pads to scren
		map_pad.noutrefresh(0, 0, 0, 0, game_map._size[1], game_map._size[0])
		message_log_pad.noutrefresh(0, 0, game_map._size[1], 0, game_map._size[1] + 3, game_map._size[0])

		# Update
		self._app._screen.move(20, 0)
		curses.doupdate()
