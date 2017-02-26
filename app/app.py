# Andrew Bogdan
# Feasible Game 3
# Version 0.1

# Imports
import copy
import curses
import json
import os

from mirec_miskuf_json import json_loads_str

from renderer import Renderer
import default.ai

ai = {}

for var in default.ai.__all__:

	ai[var] = vars(default.ai)[var]

# Constants
DIR_NORTH = 0
DIR_NORTHEAST = 1
DIR_EAST = 2
DIR_SOUTHEAST = 3
DIR_SOUTH = 4
DIR_SOUTHWEST = 5
DIR_WEST = 6
DIR_NORTHWEST = 7

DIR_OFFSETS = { DIR_NORTH: (0, -1),
                DIR_NORTHEAST: (1, -1),
                DIR_EAST: (1, 0),
                DIR_SOUTHEAST: (1, 1),
                DIR_SOUTH: (0, 1),
                DIR_SOUTHWEST: (-1, 1),
                DIR_WEST: (-1, 0),
                DIR_NORTHWEST: (-1, -1)}

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

		# Load game options
		game_options_path = os.path.join(       os.path.dirname(__file__), 
							"options.json")
		game_options_file = open(game_options_path, 'r')
		self._options = json_loads_str(game_options_file.read())
		game_options_file.close()

		# Load renderer options
		renderer_options_path = os.path.join(   os.path.dirname(__file__),                                                              "renderer",
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

        The Game._act_* namespace is the collection of methods that actions should call.
	The Game._io_* namespace is used for various control inputs.
	The Game._mod_* namespace is used for modifying state (__init__ does it also)

	Game.__init__(self, app, options)
        Game._act_move(self, mob, direction)
        Game._do_action(self, mob, action)
	Game._io_move_north(self)
	Game._io_move_west(self)
	Game._io_move_south(self)
	Game._io_move_east(self)
	Game._io_pause(self)
	Game._mod_move(self, mob, to_coords)
	Game._turn(self)
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
		self._controls = {      "move_north": self._io_move_north,
					"move_west": self._io_move_west,
					"move_south": self._io_move_south,
					"move_east": self._io_move_east,
					"pause": self._io_pause}
		self._state = None
		# *** DEBUG ***
		path = os.path.join(    os.path.dirname(__file__), 
					"debug/state3.json")
		f = open(path, 'r')
		self._state = State(json_loads_str(f.read()))
		# *** DEUBG ***
		pass

        def _act_move(self, mob, direction):
                """
                Moves the mob 1 unit in direction so that the mob can collide.

                Perhaps this method should return something if there's a failure so action can react?
                """

                # Calculate the to_coords
                offset = DIR_OFFSETS[direction]
                to_coords = (mob.coords[0] + offset[0], mob.coords[1] + offset[1], mob.coords[2])

                # Execute the movement
                self._mod_move(mob, to_coords)

        def _do_action(self, mob, action):
                """Change state based on which action is performed by what mob."""

                # *** DEBUG ***
                path = os.path.join(os.path.dirname(__file__), *action.split(':'))
                action_file = open(path, 'r')
                exec(action_file.read())
                # *** DEBUG ***
                pass

	def _io_move_north(self):
		"""Prepare to move the player character north."""
		
		player = self._state.index[1]
		ai_type = player.ai.split(":")[-1]
		player.next_turn = ai[ai_type].DefAI.get_move(player, DIR_NORTH)

	def _io_move_west(self):
		"""Prepare to move the player character west."""

		player = self._state.index[1]
		ai_type = player.ai.split(":")[-1]
		player.next_turn = ai[ai_type].DefAI.get_move(player, DIR_WEST)

	def _io_move_south(self):
		"""Prepare to move the player character south."""

		player = self._state.index[1]
		ai_type = player.ai.split(":")[-1]
		player.next_turn = ai[ai_type].DefAI.get_move(player, DIR_SOUTH)

	def _io_move_east(self):
		"""Prepare to move the player character east."""

		player = self._state.index[1]
		ai_type = player.ai.split(":")[-1]
		player.next_turn = ai[ai_type].DefAI.get_move(player, DIR_EAST)

	def _io_pause(self):
		"""Quit the game."""

                # *** DEBUG ***
		self._app.stop()
                # *** DEBUG ***

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

        def _turn(self):
                """Execute the actions of a turn"""

                # Execute all of the actions
                for mob in self._state.map.get_mobs():

                        self._do_action(mob, mob.next_turn)

                # Reset/decide the actions for all the next turns
                for mob in self._state.map.get_mobs():

                        ai_type = mob.ai.split(":")[-1]
                        mob.next_turn = ai[ai_type].DefAI.get_next_turn(mob)

	def eval_control_string(self, string):
		"""Evaluate a control string, mapping it to a Game._io_* function."""

		self._controls[string]()

	def loop(self):
		"""Perform a main game loop."""

                will_do_turn = True

		for mob in self._state.map.get_mobs():
                        if mob.next_turn == None:

                                will_do_turn = False

                if will_do_turn:

                        self._turn()

class State(object):
	"""
	The class which contains all the in-game information necessary to take a snapshot

	State.__init__(self, saved_state)
	State.__str__(self)

	State.map
	State.index
	"""

	def __init__(self, saved_state):
		"""
                Initialize the State from a save.

                Member variables have free reign to edit saved_state.
                """

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
        Map.get_mobs(self)

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

	def get_mobs(self):
                """Return all the mobs in the map."""

                mob_list = []

                for col in self.grid:
                        for tile in col:

                                mob_list.extend(tile.get_mobs())

                return mob_list

class Tile(object):
	"""
	A tile on the map, potentially containing many entities

	Tile.__init__(self, saved_state, coords)
	Tile.__str__(self)
        Tile.get_mobs(self)

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

	def get_mobs(self):
                """Get all the mobs in the tile"""

                mob_list = []

                for layer in self.layers:
                        for permeability in layer.keys():
                                if type(layer[permeability]) == Mob:

                                        mob_list.append(layer[permeability])

                return mob_list

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
	Mob.__str__(self)
	Mob.get_actions(self)

	Mob._actions
	Mob.ai
	Mob.next_turn

	Also includes some member variables from Entity
	"""

	def __init__(self, saved_state, coords):
		"""
		Create a Mob from a saved state.

		You might want to send saved_state as a deepcopy, as it is modified
		"""

		# Restore Mob-only variables by popping
		self._actions = saved_state.pop("actions")
		self.ai = saved_state.pop("ai")
		self.next_turn = saved_state.pop("next_turn")

		# Do super.__init__ with the non-Mob-only variables
		super(Mob, self).__init__(saved_state, coords)

	def __str__(self):
		"""
		Create a string representation used for saving.

		self.coords is a soft reference, so it is not saved.
		"""

		state = {       "id": self.id, "permeability": self.permeability,
				"ai": self.ai, "next_turn": self.next_turn,
				"actions": self._actions}

		return json.dumps(state)

	def get_actions(self):
                """Return the mob's actions."""

                return self._actions

# Functions

def directory_from_id(id_):

	return os.path.join(id_.split(':'))
