# Andrew Bogdan
# Feasible Game 3
# Version 0.1

# Imports
import copy
import curses
import json
import os
from console_renderer import Renderer

from mirec_miskuf_json import *

# Constants
VIEW_MAP = 0
VIEW_DC = 1

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

		# Load options
		game_options_file = open("options.json", 'r')
		self._options = json_loads_str(game_options_file.read())
		game_options_file.close()

		renderer_options_file = open(os.path.join("console_renderer", "options.json"), 'r')
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
		self._screen.nodelay(1)
		self._screen.keypad(1)

	def _loop(self):
		"""Perform a main game loop."""

		# Loop the subclasses
		self._game.loop()
		self._renderer.loop()

		# Get and evaluate I/O
		key = self._screen.getch()

		if str(key) in self._options["controls"] and key != curses.ERR:

			self._game.eval_control_string(self._options["controls"][str(key)])

	def _quit(self):
		"""Clean up and shut down the app."""

		# Shut down curses
		self._screen.keypad(0)
		self._screen.nodelay(0)
		curses.nocbreak()
		curses.echo()
		curses.endwin()

	def stop(self):
		"""Stop looping."""

		self._is_running = False

	def start(self):
		"""Start looping."""

		# Loop
		self._is_running = True

		while self._is_running:

			self._loop()

		# Quit when the loop stops
		self._quit()

class Game(object):
	"""
	The class which controls the game, doing modifications on the game state

	The Game._io_* namespace is used for various control inputs.
	The Game._mod_* namespace is used for modifying state (__init__ does it also)

	Game.__init__(self, app, options)
	Game._io_move_north(self)
	Game._io_move_west(self)
	Game._io_move_south(self)
	Game._io_move_east(self)
	Game._io_pause(self)
	Game._mod_move(self, mob, to_coords)
	Game.eval_control_string(self, string)
	Game.loop(self)

	Game._app
	Game._controls
	Game._state
	"""

	def __init__(self, app, options):
		"""Initialize Game, starting the game."""

		# Initialize variables
		self._app = app
		self._controls = {	"move_north": self._io_move_north,
					"move_west": self._io_move_west,
					"move_south": self._io_move_south,
					"move_east": self._io_move_east,
					"pause": self._io_pause}
		self._state = None
		# *** DEBUG ***
		f = open("debug/state.json", 'r')
		self._state = State(json_loads_str(f.read()))
		# *** DEUBG ***

		pass

	def _io_move_north(self):
		"""Move the player character north."""
		
		# *** DEBUG ***
		print "north"
		# *** DEBUG ***
		pass

	def _io_move_west(self):
		"""Move the player character west."""

		# *** DEBUG ***
		print "west"
		# *** DEBUG ***
		pass

	def _io_move_south(self):
		"""Move the player character south."""

		# *** DEBUG ***
		print "south"
		# *** DEBUG ***
		pass

	def _io_move_east(self):
		"""Move the player character east."""

		# *** DEBUG ***
		print "east"
		# *** DEBUG ***
		pass

	def _io_pause(self):
		"""Quit the game."""

		self._app.stop()

	def _mod_move(self, entity, to_coords):
		"""
		Attempt to move entity to specified coordinates.

		This is the only method allowed to move entities
		It specifies entity to prevent referencing empty coordinates.
		It also changes entity.coords
		It also expands tile if necessary
		You might want to copy.copy(...) to_coords before using this.
		"""
		
		# Get the from and to loactions
		from_layers = self._state.map.grid[entity.coords[0]][entity.coords[1]].layers
		to_layers = self._state.map.grid[to_coords[0]][to_coords[1]].layers

		try:
			if min(to_layers[to_coords[2]].keys()) <= entity.permeability:

				# A collision has occurred
				return

		except IndexError:

			# Entity is moving to a vaccuum above the defined layers
			pass

		except ValueError:

			# Entity is moving into a vaccuum under some defined layer
			pass

		# Remove the entity
		del from_layers[entity.coords[2]][entity.permeability]
		
		# Clean up; this would add the default tile (?) if that were implemented
		while from_layers[-1] == {} and len(from_layers) != 0:

			del from_layers[-1]

		# Put the entity at the new location, extending with default tile (!) if necessary
		while len(to_layers) <= to_coords[2]:

			to_layers.append({})

		to_layers[to_coords[2]][entity.permeability] = entity

		# Fix entity.coords
		entity.coords = to_coords

	def eval_control_string(self, string):
		"""Evaluate a control string, mapping it to a Game._io_* function."""

		self._controls[string]()

	def loop(self):
		"""Perform a main game loop."""

		pass

class State(object):
	"""
	The class which contains all the in-game information necessary to take a snapshot

	State.__init__(self, saved_state)
	State.__str__(self)

	State.map
	State.index
	"""

	def __init__(self, saved_state):
		"""Initialize the State from a save."""

		# Load from the saved state
		self.map = Map(saved_state["map"])
		
		# Load index
		self.index = saved_state["index"]

		if saved_state["index"][0] == VIEW_MAP or saved_state["index"][0] == VIEW_DC:

			mob_loc_x = saved_state["index"][1][0][0]
			mob_loc_y = saved_state["index"][1][0][1]
			mob_layer = saved_state["index"][1][0][2]
			mob_permeability = saved_state["index"][1][1]

			tile = self.map.grid[mob_loc_x][mob_loc_y]
			layer = tile.layers[mob_layer]
			mob = layer[mob_permeability]

			self.index[1] = mob

	def __str__(self):
		"""Create a string representation used for saving."""

		# Check if index[1] is a mob and then fix it if necessary
		if type(self.index[1]) == Mob:

			saved_index = copy.copy(self.index)

			saved_index[1] = [self.index[1].coords, self.index[1].permeability]

		# Construct the state and return
		state = {"map": json_loads_str(str(self.map)), "index": saved_index}

		return json.dumps(state)

class Map(object):
	"""
	The class which contains a grid of tiles

	Map.__init__(self, saved_state)
	Map.__str__(self)

	Map._size
	Map.grid
	"""

	def __init__(self, saved_state):
		"""Initialize the Map from a saved state."""

		# Load from the saved state
		self._size = tuple(saved_state["size"])

		# Load the grid
		self.grid = []

		for x_val in range(len(saved_state["grid"])):

			saved_col = saved_state["grid"][x_val]
			col = []

			for y_val in range(len(saved_col)):

				saved_tile = saved_state["grid"][x_val][y_val]
				col.append(Tile(saved_tile, [x_val, y_val]))

			self.grid.append(col)

	def __str__(self):
		"""Create a string representation used for saving."""

		# Fix grid
		saved_grid = []

		for col in self.grid:

			saved_col = []

			for tile in col:

				saved_col.append(json_loads_str(str(tile)))

			saved_grid.append(saved_col)

		# Construct the state and return
		state = {"size": self._size, "grid": saved_grid}

		return json.dumps(state)

class Tile(object):
	"""
	A tile on the map, potentially containing many entities

	Tile.__init__(self, saved_state, coords)
	Tile.__str__(self)

	Tile.coords
	Tile.layers
	"""

	def __init__(self, saved_state, coords):
		"""Load the Tile from a saved state."""

		# Set coords
		self.coords = coords

		# Reconstruct layers and entites
		self.layers = []
		layers_list = saved_state["layers"]

		for layer_dict in layers_list:

			layer = {}

			for key in layer_dict:

				entity_coords = copy.copy(coords)
				entity_coords.append(int(key))

				if layer_dict[key][0] == "mob":

					layer[int(key)] = Mob(layer_dict[key][1], entity_coords)

				elif layer_dict[key][0] == "nonmob":

					layer[int(key)] = NonMob(layer_dict[key][1], entity_coords)

			self.layers.append(layer)
		
	def __str__(self):
		"""
		Create a string representation used for saving.

		self.coords is not saved because it is a soft reference.
		"""

		# Fix layers
		layers_list = []

		for layer in self.layers:

			layer_dict = {}

			for key in layer:
				# Check if it's a Mob or NonMob
				if type(layer[key]) == Mob:

					layer_dict[key] = ["mob", json_loads_str(str(layer[key]))]

				elif type(layer[key]) == NonMob:

					layer_dict[key] = ["nonmob", json_loads_str(str(layer[key]))]

			layers_list.append(layer_dict)

		# Construct the state and return
		state = {"layers": layers_list}

		return json.dumps(state)
		

class Entity(object):
	"""
	An entity, what is occupying a tile

	Higher permeability means it's more similar to a vaccuum.

	Entity.__init__(self, saved_state, coords)
	Entity.__str__(self)

	Entity.coords
	Entity.id
	Entity.permeability
	"""

	def __init__(self, saved_state, coords):
		"""Load the Entity from a saved state dict."""

		# Reconstruct
		self.coords = coords
		self.id = saved_state["id"]
		self.permeability = saved_state["permeability"]

	def __str__(self):
		"""
		Create a string representation used for saving.

		self.coords is a soft reference, so it is not saved.
		"""

		state = {"id": self.id, "permeability": self.permeability}

		return json.dumps(state)

class NonMob(Entity):
	"""
	An entity wihout an AI

	NonMob.__init__(self, saved_state, coords)

	Also includes some member variables from Entity
	"""

	def __init__(self, saved_state, coords):
		"""Create a NonMob from a saved state."""

		super(NonMob, self).__init__(saved_state, coords)

class Mob(Entity):
	"""
	An entity with an AI

	Mob.__init__(self, saved_state, coords)

	Also includes some member variables from Entity
	"""

	def __init__(self, saved_state, coords):
		"""Create a Mob from a saved state."""

		super(Mob, self).__init__(saved_state, coords)

# Functions

def directory_from_id(id_):

	return os.path.join(id_.split(':'))

# Main

app = App()
app.start()
