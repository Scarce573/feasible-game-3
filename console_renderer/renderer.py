# Andrew Bogdan
# Console Renderer
# Version 0.1

# Modules
import curses
import os
from mirec_miskuf_json import *

# Classes

class Renderer:
	"""
	A renderer which uses curses to render onto a console.

	Renderer.__init__(self)
	Renderer._make_map(self)
	Renderer.loop(self)

	Renderer._app
	Renderer._chracter_key
	Renderer._options
	"""

	def __init__(self, app, options):
		"""Intialize the Renderer."""

		# Initialize variables
		self._app = app
		self._options = options

		# Get id to character dict
		character_key_file = open(os.path.join("console_renderer", "character_key.json"), 'r')
		self._character_key = json_loads_str(character_key_file.read())
		character_key_file.close()

	def _make_map(self, game_map):

		# Make a pad for map
		map_pad = curses.newpad(game_map._size[1], game_map._size[0])
		
		# Construct the map pad
		for y_val in range(0, game_map._size[1]):
		    for x_val in range(0, game_map._size[0]):

			tile_to_render = game_map.grid[x_val][y_val]

			# *** DEBUG ***
			perm = min(tile_to_render.layers[-1].keys())
			entity_to_render = tile_to_render.layers[-1][perm]
                        # *** DEBUG ***

			ch = self._character_key[entity_to_render.id][0]

			try:

			    map_pad.addch(y_val, x_val, ch)

			except curses.error:

			    pass

		# Return the map pad
		return map_pad

	def loop(self):

		# Load information
		game_map = self._app._game._state._map

		# Get pads
		map_pad = self._make_map(game_map)

		# Print pads to scren
		map_pad.refresh(0, 0, 0, 0, game_map._size[1], game_map._size[0])
