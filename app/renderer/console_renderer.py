# Andrew Bogdan
# Console Renderer
# Version 0.1

# Modules
import curses
import os

from mirec_miskuf_json import json_loads_str

from ..renderer_super import Renderer

# Constants
VIEW_MAP = 0
VIEW_DC = 1
VIEW_PAUSE = 2

# Classes
class ConsoleRenderer(Renderer):
	"""
	A renderer which uses curses to render onto a console.

	Renderer.__init__(self)
	Renderer._make_map(self, game_map)
	Renderer._make_message_log(self, game_message_log)
	Renderer._view_coag(self)
	Renderer._view_map(self)
	Renderer.loop(self)

	Renderer._app
	Renderer._change_flag
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

		# Etc
		self._change_flag = VIEW_MAP

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

	def _view_coag(self, root_level=0):
		
		# Load information
		game_index = self._app._game._state.index
		# *** DEBUG ***
		vis_depth = 2
		vis_number = 15
		focus_index = 7
		col_width = 16
		desc_width = 32
		# *** DEBUG ***

		# Make a pad for each column
		pads = []

		for depth in range(vis_depth):

			# Get each coagulate and generate the names/items to print
			# If you can't go that far back, continue
			try: coag = self._app._game._deref_index(game_index[:-depth - 1])
			except IndexError: continue
			# Find the index in the coagulate which should be highlighted
			focus = game_index[-depth - 1]
			# Construct all the names
			all_items = []

			for item in coag:

				all_items.append(item.name)

			# Find the section (items) of the names which should be selected
			# Offset should be added to an index to make it the effective index
			upper = focus + (vis_number - focus_index - 1)
			lower = focus - (focus_index - 1)

			if lower <= 0: 

				offset = 0

			elif upper >= len(coag): 

				offset = len(coag) - min(vis_number, len(coag))

			else: 

				offset = focus - focus_index

			# Build the pad
			col_pad = curses.newpad(vis_number + 1, col_width)
			col_pad.addstr(0, 0, coag.name, curses.A_BOLD)

			for row in range(vis_number):

				if row + offset == focus:

					try: col_pad.addstr(row + 1, 0, all_items[row + offset], curses.A_STANDOUT)
					except IndexError: pass

				else:

					try: col_pad.addstr(row + 1, 0, all_items[row + offset])
					except IndexError: pass

			pads.append(col_pad)

		# Build up pads list and add empty pads
		pads.reverse()

		while len(pads) < vis_depth:

			pads.append(curses.newpad(vis_number + 1, col_width))

		# Add the descriptor pad
		if len(self._app._game._deref_index(game_index)) == 0:

			desc_pad = curses.newpad(vis_number + 1, desc_width)

			info = " ".join(str(self._app._game._deref_index(game_index)).split("    "))
			info = info.split('\n')

			for line in range(min(vis_number, len(info))):

				desc_pad.addstr(line, 0, info[line])

			pads.append(desc_pad)

		else:

			pads.append(curses.newpad(vis_number + 1, desc_width))

		# Render everything but the last pad
		for col in range(len(pads) - 1):
			
			pads[col].noutrefresh(0, 0, 0, col_width * col, col_width, col_width * (col + 1))

		# Render the desc_pad or its empty replacement
		pads[-1].noutrefresh(0, 0, 0, col_width * (len(pads) - 1), col_width, col_width * (len(pads) - 1) + desc_width)

	def _view_map(self):

		# Load information
		game_map = self._app._game._state.map
		game_message_log = self._app._game._state.message_log

		# Get pads
		map_pad = self._make_map(game_map)
		message_log_pad = self._make_message_log(game_message_log)

		# Print pads to scren
		map_pad.noutrefresh(0, 0, 0, 0, game_map._size[1], game_map._size[0])
		message_log_pad.noutrefresh(0, 0, game_map._size[1], 0, game_map._size[1] + 3, game_map._size[0])

	def loop(self):

		# Call super.loop, which is unnecessary for now but good form
		super(ConsoleRenderer, self).loop()

		if self._app._game._state.index[0] == VIEW_MAP:

			self._view_map()

			if self._change_flag != VIEW_MAP:

				self._change_flag = VIEW_MAP
				self._app._screen.redrawwin()

		elif self._app._game._state.index[0] == VIEW_DC:

			self._view_coag(root_level=1)

			if self._change_flag != VIEW_DC:

				self._change_flag = VIEW_DC
				self._app._screen.redrawwin()

		elif self._app._game._state.index[0] == VIEW_PAUSE:

			self._view_coag(root_level=0)

			if self._change_flag != VIEW_PAUSE:

				self._change_flag = VIEW_PAUSE
				self._app._screen.redrawwin()
		
		# Update
		self._app._screen.move(20, 0)
		curses.doupdate()
