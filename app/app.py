# Andrew Bogdan
# Feasible Game 3
# Version 0.2

# Imports
import copy
import curses
import json
import os
import pprint

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

FOCUS_MAP = 0
FOCUS_CONSOLE = 1

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
	Game._build_controls(self)
	Game._do_action(self, mob, action)
	Game._io_console_echo(self, char)
	Game._io_console_input(self)
	Game._io_console_submit(self)
	Game._io_move_north(self)
	Game._io_move_west(self)
	Game._io_move_south(self)
	Game._io_move_east(self)
	Game._io_pause(self)
	Game._mod_change_index(self, index, to_value)
	Game._mod_console_add_char(self, char)
	Game._mod_console_new_message(self)
	Game._mod_console_run_message(self)
	Game._mod_move(self, mob, to_coords)
	Game._mod_set_next_turn(self, mob, action)
	Game._turn(self)
	Game.eval_control_string(self, string)
	Game.eval_echo(self, char)
	Game.loop(self)

	Game._app
	Game._controls
	Game._state
	"""

	def __init__(self, app, options):
		"""Initialize Game, starting the game."""

		# Initialize variables
		self._app = app		

		self._state = None
		# *** DEBUG ***
		path = os.path.join(	os.path.dirname(__file__), 
								"debug/state.json")
		with open(path, 'r') as state_file:

			self._state = State(json_loads_str(state_file.read()))
		# *** DEUBG ***
		
		# Build controls
		self._build_controls()

		# Give mobs their first turn
		for mob in self._state.map.get_mobs():

			ai_type = mob.ai.split(':')[-1]
			self._mod_set_next_turn(mob, ai[ai_type].DefAI.get_next_turn(self._state.map, mob))

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

	def _build_controls(self):
		"""
		Build the controls based off of index.

		This is the only function which can edit self._controls.
		"""

		# The controls for the map view
		if self._state.index[0] == VIEW_MAP:

			# You're interacting with the map
			if self._state.index[2] == FOCUS_MAP:

				self._controls = {	"move_north": self._io_move_north,
									"move_west": self._io_move_west,
									"move_south": self._io_move_south,
									"move_east": self._io_move_east,
									"pause": self._io_pause,
									"console_submit": None,
									"console_input": self._io_console_input,
									"_echo": None}

			# You're interacting with the conosle
			if self._state.index[2] == FOCUS_CONSOLE:

				self._controls = {	"move_north": None,
									"move_west": None,
									"move_south": None,
									"move_east": None,
									"pause": None,
									"console_submit": self._io_console_submit,
									"console_input": None,
									"_echo": self._io_console_echo}

	def _do_action(self, mob, action):
		"""Change state based on which action is performed by what mob."""

		# *** DEBUG ***
		path = _path_from_id(action)
		action_file = open(path, 'r')
		exec(action_file.read())
		# *** DEBUG ***
		pass

	def _io_console_echo(self, char):
		"""Deal with with echo character input."""

		self._mod_console_add_char(char)

	def _io_console_input(self):
		"""Switch index to input into the console."""

		self._mod_change_index(2, FOCUS_CONSOLE)
		self._mod_console_new_message()

	def _io_console_submit(self):
		"""Run the command currently at the bottom of the message log"""

		self._mod_change_index(2, FOCUS_MAP)
		self._mod_console_run_message()

	def _io_move_north(self):
		"""Prepare to move the player character north."""
		
		player = self._state.index[1]
		ai_type = player.ai.split(':')[-1]
		self._mod_set_next_turn(player, ai[ai_type].DefAI.get_move(player, DIR_NORTH))

	def _io_move_west(self):
		"""Prepare to move the player character west."""

		player = self._state.index[1]
		ai_type = player.ai.split(':')[-1]
		self._mod_set_next_turn(player, ai[ai_type].DefAI.get_move(player, DIR_WEST))

	def _io_move_south(self):
		"""Prepare to move the player character south."""

		player = self._state.index[1]
		ai_type = player.ai.split(':')[-1]
		self._mod_set_next_turn(player, ai[ai_type].DefAI.get_move(player, DIR_SOUTH))

	def _io_move_east(self):
		"""Prepare to move the player character east."""

		player = self._state.index[1]
		ai_type = player.ai.split(':')[-1]
		self._mod_set_next_turn(player, ai[ai_type].DefAI.get_move(player, DIR_EAST))

	def _io_pause(self):
		"""Pause the game, also known as quit the game (for now)"""

		# *** DEBUG ***
		self._app.stop()
		# *** DEBUG ***

	def _mod_change_index(self, index, to_value):
		"""Change self._state.index safely."""

		self._state.index[index] = to_value
		self._build_controls()

	def _mod_console_add_char(self, char):
		"""Add a character to the console."""

		self._state.message_log[-1] = self._state.message_log[-1] + char

	def _mod_console_new_message(self):
		"""Begin a new message in the console."""

		self._state.message_log.append("> ")

	def _mod_console_run_message(self):
		"""Run the current console message."""

		self._state.message_log[-1] = self._state.message_log[-1][2:]

		try:

			exec(self._state.message_log[-1])

		except SyntaxError:

			pass

		except NameError:

			pass

		except:

			self._state.message_log.append("Error!")

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

	def _mod_set_next_turn(self, mob, action):
		"""Set the next turn of the mob."""

		mob.next_turn = action

	def _turn(self):
		"""Execute the actions of a turn"""

		# Execute all of the actions
		for mob in self._state.map.get_mobs():

			self._do_action(mob, mob.next_turn)

		# Reset/decide the actions for all the next turns
		for mob in self._state.map.get_mobs():

			ai_type = mob.ai.split(':')[-1]
			self._mod_set_next_turn(mob, ai[ai_type].DefAI.get_next_turn(self._state.map, mob))

	def eval_control_string(self, string):
		"""
		Evaluate a control string, mapping it to a Game._io_* function.


		Returns True or False to tell App if it did anything. That lets it know if it 
		should continue processing the input.
		"""

		if self._controls[string]:

			self._controls[string]()
			return True

		else:

			# The action is unbound right now, so tell the game to find another method to call
			return False

	def eval_echo(self, char):
		"""
		Evaluate a character text input.

		The "_echo" control string is reserved for this function.
		"""

		if self._controls["_echo"]:

			self._controls["_echo"](char)

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

	State.__init__(self, saved_state=None)
	State.__repr__(self)
	State.__str__(self)
	State.to_dict(self)

	State.map
	State.message_log
	State.index
	"""

	def __init__(self, saved_state=None):
		"""
		Initialize the State from a save.

		Member variables have free reign to edit saved_state.
		"""

		if saved_state:

			# Load from the saved state
			self.map = load_from_dict(saved_state["map"])
			self.message_log = saved_state["message_log"]
			
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

	def __repr__(self):
		"""Return a syntactically correct string representation of the State based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the State based off of to_dict."""

		return json.dumps(self.to_dict())

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the State."""

		state = {}

		# Fix index[1] if necessary
		saved_index = copy.copy(self.index)

		if type(self.index[1]) == Mob:

			saved_index[1] = [self.index[1].coords, self.index[1].permeability]

		# Construct state
		state["_type"] = "State"
		state["index"] = saved_index
		state["map"] = self.map.to_dict()
		state["message_log"] = self.message_log

		# Return state
		return state

class Map(object):
	"""
	The class which contains a grid of tiles

	Map.__init__(self, saved_state=None)
	Map.__repr__(self)
	Map.__str__(self)
	Map.get_mobs(self)
	Map.to_dict(self)

	Map._size
	Map.grid
	"""

	def __init__(self, saved_state=None):
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
				col.append(load_from_dict(saved_tile, [x_val, y_val]))

			self.grid.append(col)

	def __repr__(self):
		"""Return a syntactically correct string representation of the Map based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the Map based off of to_dict."""

		return json.dumps(self.to_dict())

	def get_mobs(self):
		"""Return all the mobs in the Map."""

		mob_list = []

		for col in self.grid:
			for tile in col:

				mob_list.extend(tile.get_mobs())

		return mob_list

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Map."""

		state = {}

		# Fix grid
		saved_grid = []

		for col in self.grid:

			saved_col = []

			for tile in col:

				saved_col.append(tile.to_dict())

			saved_grid.append(saved_col)

		# Construct state
		state["_type"] = "Map"
		state["grid"] = saved_grid
		state["size"] = self._size

		# Return state
		return state

class Tile(object):
	"""
	A tile on the map, potentially containing many entities

	Tile.__init__(self, coords = [-1, -1], saved_state=None)
	Tile.__repr__(self)
	Tile.__str__(self)
	Tile.get_mobs(self)
	Tile.to_dict(self)

	Tile.coords
	Tile.layers
	"""

	def __init__(self, coords=[-1, -1], saved_state=None):
		"""Initialize the Tile, perhaps from a saved state."""

		if saved_state:

			# Loading from a saved_state dict
			# Construct layers
			self.layers = []

			saved_layers_list = saved_state["layers"]

			for saved_layer_dict in saved_layers_list:

				layer = {}

				for key in saved_layer_dict:

					entity_coords = copy.copy(coords)
					entity_coords.append(int(key))

					layer[int(key)] = load_from_dict(saved_layer_dict[key], entity_coords)

				self.layers.append(layer)

		else:

			pass

		self.coords = coords

	def __repr__(self):
		"""Return a syntactically correct string representation of the Tile based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the Tile based off of to_dict."""

		return json.dumps(self.to_dict())

	def get_mobs(self):
		"""Get all the mobs in the tile"""

		mob_list = []

		for layer in self.layers:
			for permeability in layer.keys():
				if type(layer[permeability]) == Mob:

					mob_list.append(layer[permeability])

		return mob_list

	def to_dict(self):
		"""
		Create a JSON-serializable dict representation of the Tile.

		self.coords is not saved because it is a soft reference.
		"""

		state = {}

		# Fix layers
		saved_layers = []

		for layer in self.layers:

			saved_layer_dict = {}

			for key in layer:
				
				saved_layer_dict[str(key)] = layer[key].to_dict()

			saved_layers.append(saved_layer_dict)

		# Construct state
		state["_type"] = "Tile"
		state["layers"] = saved_layers

		# Return state
		return state

class Entity(object):
	"""
	An entity, what is occupying a tile

	Higher permeability means it's more similar to a vaccuum.

	Entity.__init__(self, coords=[-1, -1, -1], saved_state=None)
	Entity.__repr__(self)
	Entity.__str__(self)
	Entity.to_dict(self)

	Entity.coords
	Entity.id
	Entity.permeability
	"""

	def __init__(self, coords=[-1, -1, -1], saved_state=None):
		"""Initialize the Entity, perhaps from a saved state."""

		if saved_state:

			# Loading from a saved_state dict
			self.id = saved_state["id"]
			self.permeability = saved_state["permeability"]

		else:

			pass

		self.coords = coords

	def __repr__(self):
		"""Return a syntactically correct string representation of the Entity based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the Entity based off of to_dict."""

		return json.dumps(self.to_dict())

	def to_dict(self):
		"""
		Create a JSON-serializable dict representation of the Entity.

		self.coords is a soft reference, so it is not saved.
		"""

		state = {}

		# Construct state
		state["_type"] = "Entity"
		state["id"] = self.id
		state["permeability"] = self.permeability

		# Return state
		return state

class NonMob(Entity):
	"""
	An entity wihout an AI

	NonMob.__init__(self, coords=[-1, -1, -1], saved_state=None)
	NonMob.to_dict(self)

	Also includes some member variables from Entity
	"""

	def __init__(self, coords=[-1, -1, -1], saved_state=None):
		"""Initialize the NonMob, perhaps from a saved state."""

		super(NonMob, self).__init__(coords, saved_state)

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the NonMob."""

		state = super(NonMob, self).to_dict()

		# Construct state
		state["_type"] = "NonMob"

		# Return state
		return state

class Mob(Entity):
	"""
	An entity with an AI

	Mob.__init__(self, coords=[-1, -1, -1], saved_state=None)
	Mob.__repr__(self)
	Mob.__str__(self)
	Mob.get_actions(self)
	Mob.to_dict(self)

	Mob._actions
	Mob.ai
	Mob.next_turn

	Also includes some member variables from Entity
	"""

	def __init__(self, coords=[-1, -1, -1], saved_state=None):
		"""Initialize the Mob, perhaps from a saved state."""

		super(Mob, self).__init__(coords, saved_state)

		if saved_state:

			# Loading from a saved_state dict
			self._actions = saved_state["actions"]
			self.ai = saved_state["ai"]
			self.next_turn = saved_state["next_turn"]

		else:

			pass

	def __repr__(self):
		"""Return a syntactically correct string representation of the Mob based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the Mob based off of to_dict."""

		return json.dumps(self.to_dict())

	def get_actions(self):
		"""Return the mob's actions."""

		return self._actions

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Mob."""

		state = super(Mob, self).to_dict()

		# Construct state
		state["_type"] = "Mob"
		state["actions"] = self._actions
		state["ai"] = self.ai
		state["next_turn"] = self.next_turn

		# Return state
		return state

class Coagulate(object):
	"""
	The unit of inventory organization; it's effectively a fun list.
	Everything in a Coagulate must be either of the type Differentia or Coagulate.

	Coagulate.__getitem__(self, index)
	Coagulate.__init__(self, name="", tree=[], saved_state=None)
	Coagulate.__repr__(self)
	Coagulate.__str__(self)
	Coagulate.to_dict(self)

	Coagulate._tree
	Coagulate.name
	"""

	def __getitem__(self, index):
		"""Get the item from Coagulate._tree at index."""

		return self._tree[index]

	def __init__(self, name="", tree=[], saved_state=None):
		"""
		Initialize the Coagulate, perhaps from a saved state.

		It does not use load_from_dict() on anything not in saved_state
		"""

		if saved_state:

			# Loading from a saved_state dict
			self.name = saved_state["name"]

			# Construct tree
			self._tree = []

			for differentia in saved_state["tree"]:

				self._tree.append(load_from_dict(differentia))

		else:

			self._tree = tree
			self.name = name

	def __repr__(self):
		"""Return a syntactically correct string representation of the Coagulate based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the Coagulate based off of to_dict."""

		return json.dumps(self.to_dict())

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Coagulate."""

		state = {}

		# Fix tree
		saved_tree = []

		for differentia in self._tree:

			saved_tree.append(differentia.to_dict())

		# Construct state
		state["_type"] = "Coagulate"
		state["tree"] = saved_tree
		state["name"] = self.name

		# Return state
		return state

class Differentia(object):
	"""
	Anything which goes inside of a coagulate.
	
	Differentia.__getitem__(self, index)
	Differentia.__init__(self, name="", method=lambda: None, saved_state=None)
	Differentia.__repr__(self)
	Differentia.__str__(self)
	Differentia.to_dict(self)

	Differentia.method
	Differentia.name
	"""

	def __getitem__(self, index):
		"""Get the item from Differentia.method at index."""

		return self.method[index]

	def __init__(self, name="", method=lambda: None, saved_state=None):
		"""Initialize the Differentia, perhaps from a saved state."""

		if saved_state:

			# Loading from a saved_state dict
			self.method = load_from_dict(saved_state["method"])
			self.name = saved_state["name"]

		else:

			self.name = name
			self.method = method

	def __repr__(self):
		"""Return a syntactically correct string representation of the Differentia based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the Differentia based off of to_dict."""

		return json.dumps(self.to_dict())

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Differentia."""

		state = {}

		# Construct state
		state["_type"] = "Differentia"
		state["method"] = self.method.to_dict()
		state["name"] = self.name

		# Return state
		return state

# Functions
def _path_from_id(id_):
	"""Get a path to a file based on its ID."""

	return os.path.join(os.path.dirname(__file__), *id_.split(':'))

def load_from_dict(saved_state, *args):
	"""
	Load an instance from a dict with the "_type" key.

	Should this use copy.copy()?
	Meanwhile while I'm not using copy.copy(), it's __init__'s job to not damage saved_state.
	"""

	return globals()[saved_state["_type"]](saved_state=saved_state, *args)