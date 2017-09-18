# Andrew Bogdan
# Feasible Game 3
# Version 0.2

# Imports
import copy
import curses
import json
import os
import traceback

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
VIEW_PAUSE = 2

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

class Game(object):
	"""
	The class which controls the game, doing modifications on the game state

	The Game._act_* namespace is the collection of methods that actions should call.
	The Game._io_* namespace is used for various control inputs.
	The Game._mod_* namespace is used for modifying state (__init__ does it also); anything can call these
	The Game.co_* namespace is for Differentia.method to hold.

	Game.__init__(self, app, options)
	Game._act_move(self, mob, direction)
	Game._build_controls(self)
	Game._deref_index(self)
	Game._do_action(self, mob, action, *args)
	Game._io_coag_back(self)
	Game._io_coag_next(self)
	Game._io_coag_prev(self)
	Game._io_coag_select(self)
	Game._io_console_echo(self, char)
	Game._io_console_input(self)
	Game._io_console_submit(self)
	Game._io_menu(self)
	Game._io_move_north(self)
	Game._io_move_west(self)
	Game._io_move_south(self)
	Game._io_move_east(self)
	Game._io_pause(self)
	Game._mod_console_add_char(self, char)
	Game._mod_console_new_message(self)
	Game._mod_console_post_message(self, message)
	Game._mod_console_run_message(self)
	Game._mod_index_edit(self, index=0, to_value=None, set_all=False)
	Game._mod_index_pop(self)
	Game._mod_index_push(self, index)
	Game._mod_move(self, mob, to_coords)
	Game._mod_set_next_turn(self, mob, action)
	Game._stop(self)
	Game._turn(self)
	Game.co_do_action(self)
	Game.co_pass(self)
	Game.co_quit(self)
	Game.co_resume(self)
	Game.eval_control_string(self, string)
	Game.eval_echo(self, char)
	Game.loop(self)

	Game._app
	Game._controls
	Game._state

	WORKING:
	Game._io_pmt_back(self)
	Game._io_pmt_dir_north(self)
	Game._io_pmt_dir_west(self)
	Game._io_pmt_dir_south(self)
	Game._io_pmt_dir_east(self)
	Game._mod_prompt_input(self, input)
	Game._pend_co_do_action(self, *args)
	Game._prompt_start(self, pend_func, prompts, allow_exit=False)
	Game._prompt_back(self)
	Game.pmt_direction(self, promptspace)
	- The Game._io_pmt_* subspace is for i/o functions spectific to prompts
	- The Game._pend_* namespace is for functions which are called when a prompt finishes
	- The Game.pmt_* namespace is for functions that set the index up for a prompt
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

			self._state = load_from_dict(json_loads_str(state_file.read()))

		#path = os.path.join(	os.path.dirname(__file__), 
		#						"debug/state2.json")

		#with open(path, 'w') as state_save_file:

		#	state_save_file.write(str(self._state))
		# *** DEBUG ***
		
		# Build controls
		self._build_controls()

		# Give mobs their first turn
		for mob in self._state.map.get_mobs():

			ai_type = mob.ai.split(':')[-1]
			self._mod_set_next_turn(mob, ai[ai_type].DefAI.get_next_turn(self._state.map, mob))

	def _act_move(self, mob, direction):
		"""
		Walks the mob 1 unit in direction so that the mob can collide.

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

		# The coagulate controls
		coagulate_controls = {	"_echo": None,
								"coag_back": self._io_coag_back,
								"coag_next": self._io_coag_next,
								"coag_prev": self._io_coag_prev,
								"coag_select": self._io_coag_select,
								"console_submit": None,
								"console_input": None,
								"menu": None,
								"move_north": None,
								"move_west": None,
								"move_south": None,
								"move_east": None,
								"pause": None}

		# The controls for the map view
		if self._state.index_stack[-1][0] == VIEW_MAP:

			# You're interacting with the map
			if self._state.index_stack[-1][2] == FOCUS_MAP:

				self._controls = {	"_echo": None,
									"coag_back": None,
									"coag_next": None,
									"coag_prev": None,
									"coag_select": None,
									"console_submit": None,
									"console_input": self._io_console_input,
									"menu": self._io_menu,
									"move_north": self._io_move_north,
									"move_west": self._io_move_west,
									"move_south": self._io_move_south,
									"move_east": self._io_move_east,
									"pause": self._io_pause}

			# You're interacting with the conosle
			elif self._state.index_stack[-1][2] == FOCUS_CONSOLE:

				self._controls = {	"_echo": self._io_console_echo,
									"coag_back": None,
									"coag_next": None,
									"coag_prev": None,
									"coag_select": None,
									"console_submit": self._io_console_submit,
									"console_input": None,
									"menu": None,
									"move_north": None,
									"move_west": None,
									"move_south": None,
									"move_east": None,
									"pause": None}

		# The controls for DC view
		elif  self._state.index_stack[-1][0] == VIEW_DC:

			self._controls = coagulate_controls

		# The controls for pause view
		elif self._state.index_stack[-1][0] == VIEW_PAUSE:

			self._controls = coagulate_controls

	def _deref_index(self, index):
		"""
		Get whatever is at the end of the given index.

		This function should always return a Coagulate or a Differentia.
		"""

		if index[0] == VIEW_MAP or index[0] == VIEW_DC:
			
			coag = index[1].dif_coag

			for sub_index in index[2:]:

				coag = coag[sub_index]

			return coag

		elif index[0] == VIEW_PAUSE:

			coag = self._state.pause_coag

			for sub_index in index[1:]:

				coag = coag[sub_index]

			return coag

	def _do_action(self, mob, action, *args):
		"""Change state based on which action is performed by what mob."""

		path = _path_from_id(action.id)
		action_file = open(path, 'r')
		exec(action_file.read())
		pass

	def _io_coag_back(self):
		"""Go back into the parent of the current coagulate."""
		
		if not self._deref_index(self._state.index_stack[-1][:-1]).is_root:

			self._mod_index_edit(to_value=self._state.index_stack[-1][:-1], set_all=True)

		else:

			# You're just below root so return to what you were doing earlier
			self._mod_index_pop()

	def _io_coag_next(self):
		"""Focus on the next thing in the coagulate."""

		if len(self._deref_index(self._state.index_stack[-1][:-1])) > self._state.index_stack[-1][-1] + 1:

			self._mod_index_edit(-1, self._state.index_stack[-1][-1] + 1)

	def _io_coag_prev(self):
		"""Focus on the previous thing in the coagulate."""

		if self._state.index_stack[-1][-1] > 0:

			self._mod_index_edit(-1, self._state.index_stack[-1][-1] - 1)

	def _io_coag_select(self):
		"""Step into a Coagulate or run a Game.co_* method."""

		# The referenced Differentia has nothing below it, so call method
	 	if not len(self._deref_index(self._state.index_stack[-1])):

	 		method = self._deref_index(self._state.index_stack[-1]).method

	 		try: args = method[1:]
	 		except IndexError: args = []
			
			method[0](self, *args)

			return

		# There's still options to choose from below you, so step in.
		new_index = copy.copy(self._state.index_stack[-1])
		new_index.append(0)

		self._mod_index_edit(to_value=new_index, set_all=True)

	def _io_console_echo(self, char):
		"""Deal with with echo character input."""

		self._mod_console_add_char(char)

	def _io_console_input(self):
		"""Switch index to input into the console."""

		self._mod_index_edit(2, FOCUS_CONSOLE)
		self._mod_console_new_message()

	def _io_console_submit(self):
		"""Run the command currently at the bottom of the message log"""

		self._mod_index_edit(2, FOCUS_MAP)
		self._mod_console_run_message()

	def _io_menu(self):
		"""Go to the E-menu."""

		self._mod_index_push([VIEW_DC, self._state.index_stack[-1][1], 0])

	def _io_move_north(self):
		"""Prepare to move the player character north."""
		
		player = self._state.index_stack[-1][1]
		ai_type = player.ai.split(':')[-1]
		self._mod_set_next_turn(player, ai[ai_type].DefAI.get_move(player, DIR_NORTH))

	def _io_move_west(self):
		"""Prepare to move the player character west."""

		player = self._state.index_stack[-1][1]
		ai_type = player.ai.split(':')[-1]
		self._mod_set_next_turn(player, ai[ai_type].DefAI.get_move(player, DIR_WEST))

	def _io_move_south(self):
		"""Prepare to move the player character south."""

		player = self._state.index_stack[-1][1]
		ai_type = player.ai.split(':')[-1]
		self._mod_set_next_turn(player, ai[ai_type].DefAI.get_move(player, DIR_SOUTH))

	def _io_move_east(self):
		"""Prepare to move the player character east."""

		player = self._state.index_stack[-1][1]
		ai_type = player.ai.split(':')[-1]
		self._mod_set_next_turn(player, ai[ai_type].DefAI.get_move(player, DIR_EAST))

	def _io_pause(self):
		"""Pause the game."""

		self._mod_index_push([VIEW_PAUSE, 0])

	def _mod_console_add_char(self, char):
		"""Add a character to the console."""

		self._state.message_log[-1] = self._state.message_log[-1] + char

	def _mod_console_new_message(self):
		"""Begin a new message in the console."""

		self._state.message_log.append("> ")

	def _mod_console_post_message(self, message):

		self._state.message_log.append(message)

	def _mod_console_run_message(self):
		"""Run the current console message."""

		self._state.message_log[-1] = self._state.message_log[-1][2:]

		try:

			exec(self._state.message_log[-1])

		except SyntaxError:

			pass

		except NameError:

			pass

		except Exception as error:

			self._mod_console_post_message(str(error))

	def _mod_index_edit(self, index=0, to_value=None, set_all=False):
		"""Change self._state.index_stack[-1] safely."""

		if set_all:

			self._state.index_stack[-1] = to_value

		else:

			self._state.index_stack[-1][index] = to_value

		self._build_controls()

	def _mod_index_pop(self):
		"""Pop an index to self._state.index_stack safely."""

		index = self._state.index_stack.pop()

		self._build_controls()

		return index

	def _mod_index_push(self, index):
		"""Push an index into self._state.index_stack safely."""

		self._state.index_stack.append(index)

		self._build_controls()

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
			if min(to_layers[to_coords[2]].keys()) <= entity.quanta["default:quanta:_permeability"]:

				# A collision has occurred
				return

		except IndexError:

			# Entity is moving to a vaccuum above the defined layers
			pass

		except ValueError:

			# Entity is moving into a vaccuum under some defined layer
			pass

		# Remove the entity
		del from_layers[entity.coords[2]][int(entity.quanta["default:quanta:_permeability"])]
		
		# Clean up; this would add the default tile (?) if that were implemented
		while from_layers[-1] == {} and len(from_layers) != 0:

			del from_layers[-1]

		# Put the entity at the new location, extending with default tile (!) if necessary
		while len(to_layers) <= to_coords[2]:

			to_layers.append({})

		to_layers[to_coords[2]][int(entity.quanta["default:quanta:_permeability"])] = entity

		# Fix entity.coords
		entity.coords = to_coords

	def _mod_set_next_turn(self, mob, action):
		"""Set the next turn of the mob."""

		mob.next_turn = action

	def _stop(self):

		self._app.stop()

	def _turn(self):
		"""Execute the actions of a turn"""

		# Execute all of the actions
		for mob in self._state.map.yield_mobs():

			self._do_action(mob, *mob.next_turn)
			# Set the next turn to None to tell the game to not do their turn again
			self._mod_set_next_turn(mob, None)

		# Reset/decide the actions for all the next turns
		for mob in self._state.map.get_mobs():

			ai_type = mob.ai.split(':')[-1]
			self._mod_set_next_turn(mob, ai[ai_type].DefAI.get_next_turn(self._state.map, mob))

	def co_do_action(self, *args):
		"""Perform the clicked action next turn."""

		# Set the action to what's in focus
		player = self._state.index_stack[-1][1]
		action = [self._deref_index(self._state.index_stack[-1][:-1])]
		action.extend(args)
		self._mod_set_next_turn(player, action)

		# Go back to the map view
		self._mod_index_pop()

	def co_pass(self):
		"""Do nothing."""

		pass

	def co_quit(self):
		"""Quit the game by way of the menu."""

		self._stop()
	
	def co_resume(self):
		"""Resume the game."""

		self._mod_index_pop()

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
			if mob.next_turn == None:	# This uses "== None" because __nonzero__ isn't implemented for Action

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

	State.index_stack
	State.map
	State.message_log
	State.pause_coag
	"""

	def __init__(self, saved_state=None):
		"""
		Initialize the State, perhaps from a saved state.

		Member variables have free reign to edit saved_state.
		"""

		if saved_state:

			# Loading from a saved_state dict
			self.map = load_from_dict(saved_state["map"])
			self.message_log = saved_state["message_log"]

			# Construct index
			self.index_stack = saved_state["index_stack"]

			for index in self.index_stack:

				if index[0] == VIEW_MAP or index[0] == VIEW_DC:

					mob_loc_x = index[1][0][0]
					mob_loc_y = index[1][0][1]
					mob_layer = index[1][0][2]
					mob_permeability = index[1][1]

					tile = self.map.grid[mob_loc_x][mob_loc_y]
					layer = tile.layers[mob_layer]
					mob = layer[mob_permeability]

					index[1] = mob

		else:

			pass

		self.pause_coag = Coagulate(name="Paused",
									tree=[	Coagulate(name="Quit", method=[Game.co_quit]),
											Coagulate(name="Resume", method=[Game.co_resume])],
									is_root=True)

	def __repr__(self):
		"""Return a syntactically correct string representation of the State based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the State based off of to_dict."""

		return json.dumps(self.to_dict(), indent=4, separators=(",", ": "), sort_keys=True)

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the State."""

		state = {}

		# Fix index[1] if necessary
		saved_index_stack = copy.copy(self.index_stack)

		for saved_index in saved_index_stack:

			if type(saved_index[1]) == Mob:

				saved_index[1] = [saved_index[1].coords, int(saved_index[1].quanta["default:quanta:_permeability"])]

		# Construct state
		state["_type"] = "State"
		state["index_stack"] = saved_index_stack
		state["map"] = self.map.to_dict()
		state["message_log"] = self.message_log
		state["pause_coag"] = self.pause_coag.to_dict()

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
	Map.yield_mobs(self)

	Map._size
	Map.grid
	"""

	def __init__(self, saved_state=None):
		"""Initialize the Map, perhaps from a saved state."""

		if saved_state:

			# Loading from a saved_state dict
			self._size = tuple(saved_state["size"])

			# Construct grid
			self.grid = []

			for x_val in range(len(saved_state["grid"])):

				saved_col = saved_state["grid"][x_val]
				col = []

				for y_val in range(len(saved_col)):

					saved_tile = saved_state["grid"][x_val][y_val]
					col.append(load_from_dict(saved_tile, [x_val, y_val]))

				self.grid.append(col)

		else:

			pass

	def __repr__(self):
		"""Return a syntactically correct string representation of the Map based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the Map based off of to_dict."""

		return json.dumps(self.to_dict(), indent=4, separators=(",", ": "), sort_keys=True)

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

	def yield_mobs(self):
		"""Yield all of the mobs in order of initiative and if they have a next turn defined."""

		# Initialize to True to get the while loop started
		more_mobs = True

		while more_mobs:

			fastest_mob = None
			for mob in self.get_mobs():
				if mob.next_turn == None:

					# That mob has already moved
					pass

				elif fastest_mob == None:

					# First one is automatically the fastest until deposed
					fastest_mob = mob

				elif (	mob.quanta["default:quanta:_initiative"] + mob.next_turn[0].quanta["default:quanta:_initiative"] > 
						fastest_mob.quanta["default:quanta:_initiative"] + fastest_mob.next_turn[0].quanta["default:quanta:_initiative"]):

					fastest_mob = mob

			if fastest_mob == None:

				more_mobs = False

			else:

				yield fastest_mob

class Tile(object):
	"""
	A tile on the map, potentially containing many entities

	Tile.__init__(self, coords=(-1, -1), saved_state=None)
	Tile.__repr__(self)
	Tile.__str__(self)
	Tile.get_mobs(self)
	Tile.to_dict(self)

	Tile.coords
	Tile.layers
	"""

	def __init__(self, coords=(-1, -1), saved_state=None):
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

		return json.dumps(self.to_dict(), indent=4, separators=(",", ": "), sort_keys=True)

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

	Entity.__getattr__(self, attr)
	Entity.__init__(self, coords=(-1, -1, -1), saved_state=None)
	Entity.__repr__(self)
	Entity.__str__(self)
	Entity._find_qualita(self)
	Entity._find_quanta(self)
	Entity.to_dict(self)

	Entity.characteristics*
	Entity.coords
	Entity.dif_coag*
	Entity.id
	Entity.inventory
	Entity.knowledge
	Entity.qualita*
	Entity.quanta*
	Entity.status
	"""

	def __getattr__(self, attr):
		"""Get an attribute, but do a special behavior with dif_coag."""

		if attr == "qualita":

			return Coagulate(name="Qualita", tree=self._find_qualita())

		elif attr == "quanta":

			return Coagulate(name="Quanta", tree=self._find_quanta())

		elif attr == "characteristics":

			return Coagulate(name="Characteristics", tree=[self.qualita, self.quanta])

		elif attr == "dif_coag":

			return Coagulate(	name="Dif. Coagulate",
								tree=[	self.inventory,
										self.status,
										self.knowledge,
										self.characteristics],
								is_root=True)

		else:

			return super(Entity, self).__getattr__(attr)

	def __init__(self, coords=(-1, -1, -1), saved_state=None):
		"""Initialize the Entity, perhaps from a saved state."""

		if saved_state:

			# Loading from a saved_state dict
			self.id = saved_state["id"]
			self.inventory = load_from_dict(saved_state["inventory"])
			self.knowledge = load_from_dict(saved_state["knowledge"])
			self.status = load_from_dict(saved_state["status"])

		else:

			pass

		self.coords = coords

	def __repr__(self):
		"""Return a syntactically correct string representation of the Entity based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the Entity based off of to_dict."""

		return json.dumps(self.to_dict(), indent=4, separators=(",", ": "), sort_keys=True)

	def _find_qualita(self):
		"""Find and return the Entity's qualita."""

		qualita_list = []

		for item in self.inventory:
			for inherit_group in item.qualita_inherited:
				if eval(inherit_group[1]):

					qualita_list.append(inherit_group[0])

		for status in self.status:
			for inherit_group in status.qualita_inherited:
				if eval(inherit_group[1]):

					qualita_list.append(inherit_group[0])

		for concept in self.knowledge:
			for inherit_group in concept.qualita_inherited:
				if eval(inherit_group[1]):

					qualita_list.append(inherit_group[0])

		return qualita_list

	def _find_quanta(self):
		"""Find and return the Entity's quanta."""
		
		quanta_list = []

		for item in self.inventory:
			for inherit_group in item.quanta_inherited:

				if eval(inherit_group[1]):

					quanta_list.append(inherit_group[0])

		for status in self.status:
			for inherit_group in status.quanta_inherited:
				if eval(inherit_group[1]):

					quanta_list.append(inherit_group[0])

		for concept in self.knowledge:
			for inherit_group in concept.quanta_inherited:
				if eval(inherit_group[1]):

					quanta_list.append(inherit_group[0])

		return quanta_list

	def to_dict(self):
		"""
		Create a JSON-serializable dict representation of the Entity.

		self.coords is a soft reference, so it is not saved.
		"""

		state = {}

		# Construct state
		state["_type"] = "Entity"
		state["id"] = self.id
		state["inventory"] = self.inventory.to_dict()
		state["knowledge"] = self.knowledge.to_dict()
		state["status"] = self.status.to_dict()

		# Return state
		return state

class NonMob(Entity):
	"""
	An entity wihout an AI

	NonMob.__init__(self, coords=(-1, -1, -1), saved_state=None)
	NonMob.to_dict(self)

	Also includes some member variables from Entity
	"""

	def __init__(self, coords=(-1, -1, -1), saved_state=None):
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

	Mob.__getattr__(self, attr)
	Mob.__init__(self, coords=(-1, -1, -1), saved_state=None)
	Mob._find_actions(self)
	Mob.to_dict(self)

	Mob.actions*
	Mob.ai
	Mob.next_turn

	Also includes some member variables from Entity
	"""

	def __getattr__(self, attr):
		"""Get an attribute, but do a special behavior with dif_coag."""

		if attr == "actions":

			return Coagulate(name="Actions", tree=self._find_actions()) 

		elif attr == "dif_coag":

			return Coagulate(	name="Dif. Coagulate",
								tree=[	self.inventory,
										self.status,
										self.knowledge,
										self.characteristics,
										self.actions],
								is_root=True)		

		else:

			return super(Mob, self).__getattr__(attr)

	def __init__(self, coords=(-1, -1, -1), saved_state=None):
		"""Initialize the Mob, perhaps from a saved state."""

		super(Mob, self).__init__(coords, saved_state)

		if saved_state:

			# Loading from a saved_state dict
			self.ai = saved_state["ai"]
			self.next_turn = saved_state["next_turn"]

		else:

			pass

	def _find_actions(self):
		"""Find and return the Mob's actions."""

		action_list = []

		for item in self.inventory:
			for inherit_group in item.actions:

				if eval(inherit_group[1]):

					action_list.append(inherit_group[0])

		for status in self.status:
			for inherit_group in status.actions:
				if eval(inherit_group[1]):

					action_list.append(inherit_group[0])

		for concept in self.knowledge:
			for inherit_group in concept.actions:
				if eval(inherit_group[1]):

					action_list.append(inherit_group[0])

		return action_list

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Mob."""

		state = super(Mob, self).to_dict()

		# Construct state
		state["_type"] = "Mob"
		state["ai"] = self.ai
		state["next_turn"] = self.next_turn

		# Return state
		return state

class Coagulate(object):
	"""
	The unit of inventory organization; it's effectively a fun list.
	Everything in a Coagulate must be either of the type Differentia or Coagulate.

	Coagulate.__contains__(self, item)
	Coagulate.__getitem__(self, index)
	Coagulate.__init__(self, name="", tree=(), saved_state=None)
	Coagulate.__len__(self)
	Coagulate.__repr__(self)
	Coagulate.__str__(self)
	Coagulate.append(self, coag)
	Coagulate.to_dict(self)

	Coagulate._tree
	Coagulate.is_root
	Coagulate.method
	Coagulate.name
	"""

	def __contains__(self, item):
		"""Check if the Contains an item with that id."""

		for coag in self._tree:
			try:
				if item == coag.id:

					return True

			except AttributeError:

				pass

		return False

	def __getitem__(self, index):
		"""Get the item from Coagulate._tree at index or by id."""

		if type(index) == int:

			return self._tree[index]

		elif type(index) == str:
			for coag in self._tree:
				try:
					if index == coag.id:

						return coag

				except AttributeError:

					pass

			raise KeyError(index)

		else:

			raise TypeError("Coagulate indecies/keys must be integers/strings, not " + str(type(index))) 

	def __init__(self, name="", tree=(), method=[Game.co_pass], is_root=False, saved_state=None):
		"""
		Initialize the Coagulate, perhaps from a saved state.

		It does not use load_from_dict() on anything not in saved_state
		"""

		if saved_state:

			# Loading from a saved_state dict
			self.is_root = saved_state["is_root"]
			self.name = saved_state["name"]

			# Construct tree
			self._tree = []

			for coag in saved_state["tree"]:

				self._tree.append(load_from_dict(coag))

			# Construct method
			self.method = []

			for method in saved_state["method"]:
				if type(method) == str:
					if method.find('$') != -1:

						self.method.append(Game.__dict__[method[method.index('$') + 1:]])

				else:

					self.method.append(method)

		else:

			self._tree = tree
			self.is_root = is_root
			self.method = method
			self.name = name

	def __len__(self):
		"""Get the length of the Coagulate."""

		return len(self._tree)

	def __repr__(self):
		"""Return a syntactically correct string representation of the Coagulate based off of to_dict."""

		return repr(self.to_dict())

	def __str__(self):
		"""Return a string representation of the Coagulate based off of to_dict."""

		return json.dumps(self.to_dict(), indent=4, separators=(",", ": "), sort_keys=True)

	def append(self, coag):
		"""Add something to the Coagualte."""

		self._tree.append(coag)

	def to_dict(self):
		"""
		Create a JSON-serializable dict representation of the Coagulate.

		Coagulate.is_root is a soft reference so it isn't saved.
		"""

		state = {}

		# Fix tree
		saved_tree = []

		for coag in self._tree:

			saved_tree.append(coag.to_dict())

		# Fix method
		saved_method = []

		for method in self.method:
			if callable(method):

				saved_method.append('$' + method.__name__)

			else:

				saved_method.append(method)

		# Construct state
		state["_type"] = "Coagulate"
		state["tree"] = saved_tree
		state["is_root"] = self.is_root
		state["method"] = saved_method
		state["name"] = self.name

		# Return state
		return state

class Differentia(Coagulate):
	"""
	Any game element goes inside of a coagulate.
	
	__init__(self, name="", id_="", tree=(), method=[Game.co_pass], is_root=False, saved_state=None)
	Differentia.to_dict(self)

	Differentia.id

	Also includes some member variables from Coagulate.
	"""

	def __init__(self, name="", id_="", tree=(), method=[Game.co_pass], is_root=False, saved_state=None):
		"""Initialize the Differentia, perhaps from a saved state."""

		super(Differentia, self).__init__(name, tree, method, is_root, saved_state)

		if saved_state:

			# Loading from a saved_state dict
			self.id = saved_state["id"]	

		else:

			self.id = id_

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Differentia."""

		state = super(Differentia, self).to_dict()

		# Construct state
		state["_type"] = "Differentia"
		state["id"] = self.id

		# Return state
		return state

class Figment(Differentia):
	"""m
	A figment of the game, such as an item, status, or concept.

	Figment.__getattr__(self, attr)
	Figment.__init__(	self, name="", id_="", actions=[], qualita_inate=[], qualita_inherited=[], 
						quanta_inate=[], quanta_inherited=[], is_root=False, saved_state=None)
	Figment.to_dict(self)

	Figment.actions
	Figment.qualita_inate*
	Figment.qualita_inherited
	Figment.quanta_inate*
	Figment.quanta_inherited
	"""

	def __getattr__(self, attr):
		"""Get an attribute, but do a special behavior with inate characteristics."""

		if attr == "qualita_inate":

			return self._tree[0]

		elif attr == "quanta_inate":

			return self._tree[1]

		else:

			super(Figment, self).__getattr__(attr)

	def __init__(	self, name="", id_="", actions=[], qualita_inate=[], qualita_inherited=[], 
					quanta_inate=[], quanta_inherited=[], is_root=False, saved_state=None):
		"""Initialze the Figment, perhaps from a saved state."""

		super(Figment, self).__init__(name, id_, [], [Game.co_pass], is_root, saved_state)

		if saved_state:

			# Loading from a saved_state dict
			# Inate quanta and qualita should have already been loaded from _tree
			
			# Construct inherit lists
			self.actions = []
			self.qualita_inherited = []
			self.quanta_inherited = []

			for saved_action in saved_state["actions"]:

				action = []
				action.append(load_from_dict(saved_action[0]))
				action.extend(saved_action[1:])
				self.actions.append(action)

			for saved_qualita in saved_state["qualita_inherited"]:

				qualita = []
				qualita.append(load_from_dict(saved_qualita[0]))
				qualita.extend(saved_qualita[1:])
				self.qualita_inherited.append(qualita)

			for saved_quanta in saved_state["quanta_inherited"]:

				quanta = []
				quanta.append(load_from_dict(saved_quanta[0]))
				quanta.extend(saved_quanta[1:])
				self.quanta_inherited.append(quanta)

		else:

			self.actions = actions

			self._tree.append(Coagulate(name="Qualita",
										tree=qualita_inate,
										is_root=False))
			self.qualita_inherited = qualita_inherited

			self._tree.append(Coagulate(name="Quanta",
										tree=quanta_inate,
										is_root=False))
			self.quanta_inherited = quanta_inherited

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Figment."""

		state = super(Figment, self).to_dict()

		# Fix inherit lists
		saved_actions = []
		saved_qualita_inherited = []
		saved_quanta_inherited = []

		for action in self.actions:

			saved_action = []
			saved_action.append(action[0].to_dict())
			saved_action.extend(action[1:])
			saved_actions.append(saved_action)

		for qualita in self.qualita_inherited:

			saved_qualita = []
			saved_qualita.append(qualita[0].to_dict())
			saved_qualita.extend(qualita[1:])
			saved_qualita_inherited.append(saved_qualita)

		for quanta in self.quanta_inherited:

			saved_quanta = []
			saved_quanta.append(quanta[0].to_dict())
			saved_quanta.extend(quanta[1:])
			saved_quanta_inherited.append(saved_quanta)

		# Construct state
		state["_type"] = "Figment"
		state["actions"] = saved_actions
		state["qualita_inherited"] = saved_qualita_inherited
		state["quanta_inherited"] = saved_quanta_inherited

		# Return state
		return state

class Item(Figment):
	"""
	An item, something which can be picked up and dropped

	Item.__init__(	self, name="", id_="", actions=[], qualita_inate=[], qualita_inherited=[], 
					quanta_inate=[], quanta_inherited=[], is_root=False, saved_state=None)
	Item.to_dict(self)
	"""

	def __init__(	self, name="", id_="", actions=[], qualita_inate=[], qualita_inherited=[], 
					quanta_inate=[], quanta_inherited=[], is_root=False, saved_state=None):
		"""Initialze the Item, perhaps from a saved state."""

		super(Item, self).__init__(	name, id_, actions, qualita_inate, qualita_inherited, quanta_inate, 
									quanta_inherited, is_root, saved_state)

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Item."""

		state = super(Item, self).to_dict()

		# Construct state
		state["_type"] = "Item"

		# Return state
		return state

class Status(Figment):
	"""
	A physical descriptor of an entity

	Status.__init__(	self, name="", id_="", actions=[], qualita_inate=[], qualita_inherited=[], 
						quanta_inate=[], quanta_inherited=[], is_root=False, saved_state=None)
	Status.to_dict(self)
	"""

	def __init__(	self, name="", id_="", actions=[], qualita_inate=[], qualita_inherited=[], 
					quanta_inate=[], quanta_inherited=[], is_root=False, saved_state=None):
		"""Initialze the Status, perhaps from a saved state."""

		super(Status, self).__init__(	name, id_, actions, qualita_inate, qualita_inherited, quanta_inate, 
										quanta_inherited, is_root, saved_state)
	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Status."""

		state = super(Status, self).to_dict()

		# Construct state
		state["_type"] = "Status"

		# Return state
		return state

class Concept(Figment):
	"""
	A non-physical descriptor of an entity.

	Concept.__init__(	self, name="", id_="", actions=[], qualita_inate=[], qualita_inherited=[], 
						quanta_inate=[], quanta_inherited=[], is_root=False, saved_state=None)
	Concept.to_dict(self)
	"""

	def __init__(	self, name="", id_="", actions=[], qualita_inate=[], qualita_inherited=[], 
					quanta_inate=[], quanta_inherited=[], is_root=False, saved_state=None):
		"""Initialze the Concept, perhaps from a saved state."""

		super(Concept, self).__init__(	name, id_, actions, qualita_inate, qualita_inherited, quanta_inate, 
										quanta_inherited, is_root, saved_state)

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Concept."""

		state = super(Concept, self).to_dict()

		# Construct state
		state["_type"] = "Concept"

		# Return state
		return state

class Characteristic(Differentia):
	"""
	A single characteristic granted by a Figment

	Characteristic.__init__(self, name="", id_="", value=None, is_root=False, saved_state=None)
	Characteristic.to_dict(self)

	Characteristic._value
	"""

	def __init__(self, name="", id_="", value=None, is_root=False, saved_state=None):
		"""Initialze the Characteristic, perhaps from a saved state."""

		super(Characteristic, self).__init__(name, id_, (), [Game.co_pass], is_root, saved_state)

		if saved_state:

			# Loading from a saved_state dict
			self._value = saved_state["value"]

		else:

			self._value = value

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Characteristic."""

		state = super(Characteristic, self).to_dict()

		# Construct state
		state["_type"] = "Characteristic"
		state["value"] = self._value

		# Return state
		return state

class Qualita(Characteristic):
	"""
	A qualitative Characteristic, with a bool or str value

	Qualita.__init__(self, name="", id_="", value=True, is_root=False, saved_state=None)
	Qualita.to_dict(self)
	"""

	def __init__(self, name="", id_="", value=True, is_root=False, saved_state=None):
		"""Initialze the Qualita, perhaps from a saved state."""

		super(Qualita, self).__init__(name, id_, value, is_root, saved_state)

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Qualita."""

		state = super(Qualita, self).to_dict()

		# Construct state
		state["_type"] = "Qualita"

		# Return state
		return state

class Quanta(Characteristic):
	"""
	A quantitative Characteristic

	Quanta.__add__(self, other)
	Quanta.__eq__(self, other)
	Quanta.__floordiv__(self, other)
	Quanta.__ge__(self, other)
	Quanta.__gt__(self, other)
	Quanta.__init__(self, name="", id_="", value=0, tree=(), method=[Game.co_pass], is_root=False, saved_state=None)
	Quanta.__int__(self)
	Quanta.__le__(self, other)
	Quanta.__lt__(self, other)
	Quanta.__mod__(self, other)
	Quanta.__mul__(self, other)
	Quanta.__ne__(self, other)
	Quanta.__pow__(self, other)
	Quanta.__rfloordiv__(self, other)
	Quanta.__rmod__(self, other)
	Quanta.__rpow__(self, other)
	Quanta.__rsub__(self, other)
	Quanta.__sub__(self, other)
	Quanta.to_dict(self)
	"""

	def __add__(self, other):
		"""Add a Quanta and another Quanta or an int, returning an int."""

		if type(other) == int:

			return int(self) + other

		elif type(other) == Quanta:

			return int(self) + int(other)

		else:

			raise TypeError("unsupported operand type(s) for +: 'Quanta' and '" + str(type(other)) + "'")

	def __eq__(self, other):
		"""Check if this Quanta has equal value to an other."""

		if type(other) == int:

			return int(self) == other

		elif type(other) == Quanta:

			return int(self) == int(other)

		else:

			return NotImplemented

	def __floordiv__(self, other):
		"""Take the floored quotient of a Quanta and another Quanta or an int, returning an int."""

		if type(other) == int:

			return int(self) // other

		elif type(other) == Quanta:

			return int(self) // int(other)

		else:

			raise TypeError("unsupported operand type(s) for //: 'Quanta' and '" + str(type(other)) + "'")

	def __ge__(self, other):
		"""Check if this Quanta has a greater or equal value than an other."""

		if type(other) == int:

			return int(self) >= other

		elif type(other) == Quanta:

			return int(self) >= int(other)

		else:

			return NotImplemented

	def __gt__(self, other):
		"""Check if this Quanta has a greater value than an other."""

		if type(other) == int:

			return int(self) > other

		elif type(other) == Quanta:

			return int(self) > int(other)

		else:

			return NotImplemented

	def __init__(self, name="", id_="", value=0, is_root=False, saved_state=None):
		"""Initialze the Quanta, perhaps from a saved state."""

		super(Quanta, self).__init__(name, id_, value, is_root, saved_state)

	def __int__(self):
		"""Get an integer representation of the Quanta."""

		return int(self._value)

	def __le__(self, other):
		"""Check if this Quanta has a lesser or equal value than an other."""

		if type(other) == int:

			return int(self) <= other

		elif type(other) == Quanta:

			return int(self) <= int(other)

		else:

			return NotImplemented

	def __lt__(self, other):
		"""Check if this Quanta has a lesser value than an other."""

		if type(other) == int:

			return int(self) < other

		elif type(other) == Quanta:

			return int(self) < int(other)

		else:

			return NotImplemented

	def __mod__(self, other):
		"""Get the modulo of a Quanta and another Quanta or an int, returning an int."""

		if type(other) == int:

			return int(self) % other

		elif type(other) == Quanta:

			return int(self) % int(other)

		else:

			raise TypeError("unsupported operand type(s) for %: 'Quanta' and '" + str(type(other)) + "'")

	def __mul__(self, other):
		"""Multiply a Quanta and another Quanta or an int, returning an int."""

		if type(other) == int:

			return int(self) * other

		elif type(other) == Quanta:

			return int(self) * int(other)

		else:

			raise TypeError("unsupported operand type(s) for *: 'Quanta' and '" + str(type(other)) + "'")

	def __ne__(self, other):
		"""Check if this Quanta has unequal value to an other."""

		if type(other) == int:

			return int(self) != other

		elif type(other) == Quanta:

			return int(self) != int(other)

		else:

			return NotImplemented

	def __pow__(self, other):
		"""Take a Quanta to the power of another Quanta or an int, returning an int."""

		if type(other) == int:

			return int(self) ** other

		elif type(other) == Quanta:

			return int(self) ** int(other)

		else:

			raise TypeError("unsupported operand type(s) for **: 'Quanta' and '" + str(type(other)) + "'")

	def __rfloordiv__(self, other):
		"""Take the floored quotient a Quanta or int and this Quanta, returning an int."""

		if type(other) == int:

			return other // int(self)

		elif type(other) == Quanta:

			return int(other) // int(self)

		else:

			raise TypeError("unsupported operand type(s) for //: '" + str(type(other)) + "' and 'Quanta'")

	def __rmod__(self, other):
		"""Take the modulo of Quanta or int and this Quanta, returning an int."""

		if type(other) == int:

			return other % int(self)

		elif type(other) == Quanta:

			return int(other) % int(self)

		else:

			raise TypeError("unsupported operand type(s) for %: '" + str(type(other)) + "' and 'Quanta'")

	def __rpow__(self, other):
		"""Take a Quanta or int to the power of this Quanta, returning an int."""

		if type(other) == int:

			return other ** int(self)

		elif type(other) == Quanta:

			return int(other) ** int(self)

		else:

			raise TypeError("unsupported operand type(s) for **: '" + str(type(other)) + "' and 'Quanta'")

	def __rsub__(self, other):
		"""Subtract a Quanta or int and this Quanta, returning an int."""

		if type(other) == int:

			return other - int(self)

		elif type(other) == Quanta:

			return int(other) - int(self)

		else:

			raise TypeError("unsupported operand type(s) for -: '" + str(type(other)) + "' and 'Quanta'")

	def __sub__(self, other):
		"""Subtract a Quanta from another Quanta or an int, returning an int."""

		if type(other) == int:

			return int(self) - other

		elif type(other) == Quanta:

			return int(self) - int(other)

		else:

			raise TypeError("unsupported operand type(s) for -: 'Quanta' and '" + str(type(other)) + "'")

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Quanta."""

		state = super(Quanta, self).to_dict()

		# Construct state
		state["_type"] = "Quanta"

		# Return state
		return state

class Action(Differentia):
	"""
	A single action granted by a Figment

	Action.__getattr__(self, attr)
	Action.__init__(self, name="", id_="", tree=(), method=[Game.co_do_action], is_root=False, saved_state=None)
	Action.to_dict(self)

	Action.qualita*
	Action.quanta*
	"""
	def __getattr__(self, attr):
		"""Get an attribute, but do a special behavior with characteristics."""

		if attr == "qualita":

			return self._tree[0]

		elif attr == "quanta":

			return self._tree[1]

		else:

			super(Action, self).__getattr__(attr)

	def __init__(self, name="", id_="", qualita=[], quanta=[], meth_args=[[]], is_root=False, saved_state=None):
		"""Initialze the Action, perhaps from a saved state."""

		super(Action, self).__init__(name, id_, [], [Game.co_pass], is_root, saved_state)

		if saved_state:

			# Loading from a saved_state dict
			pass

		else:

			self._tree.append(Coagulate(name="Qualita",
										tree=qualita,
										is_root=False))
			self._tree.append(Coagulate(name="Quanta",
										tree=quanta,
										is_root=False))

			# *** DEBUG ***
			for arg in meth_args:

				
				method = [Game.co_do_action]
				method.extend(arg)
				self._tree.append(Coagulate(name="Do", method=method))
			# *** DEBUG ***

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Action."""

		state = super(Action, self).to_dict()

		# Construct state
		state["_type"] = "Action"

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