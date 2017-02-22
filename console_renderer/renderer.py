# Andrew Bogdan
# Console Renderer
# Version 0.1

# Modules
import curses
import os

# Classes

class Renderer:
	"""
	A renderer which uses curses to render onto a console.

	Renderer.__init__(self)
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
		character_key_file = open(os.path.join("console_renderer", "character_key.txt"), 'r')
		self._character_key = eval(character_key_file.read())
		character_key_file.close()

	def loop(self):

		# Get map
		game_map = self._app._game._state._map

		# Make a pad for map
		map_pad = curses.newpad(game_map._size[0], game_map._size[1])

		# Iterate and evaluate the character
		for x_val in range(game_map._size[0]):
			for y_val in range(game_map._size[1]):

				tile_to_render = game_map._grid[x_val][y_val]

                                # *** DEBUG ***
				entity_to_render = tile_to_render._layers[0][0]
                                # *** DEBUG ***

				ch = self._character_key[entity_to_render.id][0]
                                print ch
				map_pad.addch(y_val, x_val, ch)
