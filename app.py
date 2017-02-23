# Andrew Bogdan
# Feasible Game 3
# Version 0.1

# Imports
import curses
import json
import os
from console_renderer import Renderer

from mirec_miskuf_json import *

# Constants
VIEW_MAP = 0

DEFAULT_INDEX = [VIEW_MAP]

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

	Game.__init__(self, app, options)
	Game._io_move_north(self)
	Game._io_move_west(self)
	Game._io_move_south(self)
	Game._io_move_east(self)
	Game._io_pause(self)
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
		self._state = State()

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

	def eval_control_string(self, string):
		"""Evaluate a control string, mapping it to a Game._io_* function."""

		self._controls[string]()

	def loop(self):
		"""Perform a main game loop."""

		pass

class State(object):
	"""
	The class which contains all the in-game information necessary to take a snapshot

	State.__init__(self)

	State._map
	"""

	def __init__(self):

		self._map = Map()

class Map(object):
	"""
	The class which contains a grid of tiles

	Map.__init__(self)

	Map._grid
	Map._size
	"""

	def __init__(self):

		# *** DEBUG ***
		self._grid = []
		self._size = (48, 16)

		for x_val in range(self._size[0]):

			self._grid.append([])

			for y_val in range(self._size[1]):

				self._grid[x_val].append(Tile({"layers": [{"0": ["nonmob", {"permeability": 0, "id": "default:nonmob:grass"}]}, {"1": ["nonmob", {"permeability": 1, "id": "default:mob:player"}]}]}))
		# *** DEBUG ***
		pass

class Tile(object):
	"""
	A tile on the map, potentially containing many entities

	Tile.__init__(self)

	Tile._layers
	"""

	"""def __init__(self):

		self._layers = []"""

	def __init__(self, saved_state):
		"""Load the Tile from a saved state."""

		# Reconstruct layers and entites
		self._layers = []
		layers_list = saved_state["layers"]

		for layer_dict in layers_list:

			layer = {}

			for key in layer_dict:

				if layer_dict[key][0] == "mob":

					layer[key] = Mob(layer_dict[key][1])

				elif layer_dict[key][0] == "nonmob":

					layer[key] = NonMob(layer_dict[key][1])

			self._layers.append(layer)
		
	def __str__(self):
		"""Create a string representation used for saving."""

		layers_list = []

		# Iterate though layers
		for layer in self._layers:

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

	Entity.__init__(self, saved_state)
	Entity.__str__(self)

	Entity.id
	Entity.permeability
	"""

	def __init__(self, saved_state):
		"""Load the Entity from a saved state dict."""

		# Reconstruct
		self.id = saved_state["id"]
		self.permeability = saved_state["permeability"]

	def __str__(self):
		"""Create a string representation used for saving."""

		state = {"id": self.id, "permeability": self.permeability}

		return json.dumps(state)

class NonMob(Entity):
	"""
	An entity wihout an AI

	NonMob.__init__(self, saved_state)

	Also includes some member variables from Entity
	"""

	def __init__(self, saved_state):
		"""Create a NonMob from a saved state."""

		super(NonMob, self).__init__(saved_state)

class Mob(Entity):
	"""
	An entity with an AI

	Mob.__init__(self, saved_state)

	Also includes some member variables from Entity
	"""

	def __init__(self, saved_state):
		"""Create a Mob from a saved state."""

		super(Mob, self).__init__(saved_state)

# Functions

def directory_from_id(id_):

        return os.path.join(id_.split(':'))

# Main

app = App()
app.start()
