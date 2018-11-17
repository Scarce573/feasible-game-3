# Andrew Bogdan
# Feasilbe Game 3
# game.py
"""
	The class that is able to modify the state.
"""

# Imports
import os

from mirec_miskuf_json import json_loads_str

from state import *
from constants import *

import default.ai

ai = {}

for var in default.ai.__all__:

	ai[var] = vars(default.ai)[var]

# Classes
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
	Game._io_pmt_back(self)
	Game._io_pmt_dir_north(self)
	Game._io_pmt_dir_west(self)
	Game._io_pmt_dir_south(self)
	Game._io_pmt_dir_east(self)
	Game._mod_console_add_char(self, char)
	Game._mod_console_new_message(self)
	Game._mod_console_post_message(self, message)
	Game._mod_console_run_message(self)
	Game._mod_index_edit(self, index=0, to_value=None, set_all=False)
	Game._mod_index_pop(self)
	Game._mod_index_push(self, index)
	Game._mod_move(self, mob, to_coords)
	Game._mod_prompt_input(self, input)
	Game._mod_set_next_turn(self, mob, action)
	Game._pend_co_do_action(self, *args)
	Game._prompt_start(self, pend_func, prompts, allow_exit=False)
	Game._prompt_back(self)
	Game._stop(self)
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

			self._state = load_if_dict(json_loads_str(state_file.read()))

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

		# The controls
		# *** DEBUG ***
		empty_controls = {"_echo": None,
							"coag_back": None,
							"coag_next": None,
							"coag_prev": None,
							"coag_select": None,
							"console_submit": None,
							"console_input": None,
							"menu": None,
							"move_north": None,
							"move_west": None,
							"move_south": None,
							"move_east": None,
							"pause": None,
							"pmt_back": None,
							"pmt_dir_north": None,
							"pmt_dir_west": None,
							"pmt_dir_south": None,
							"pmt_dir_east": None}
		# *** DEBUG ***

		map_controls = {"_echo": None,
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
							"pause": self._io_pause,
							"pmt_back": None,
							"pmt_dir_north": None,
							"pmt_dir_west": None,
							"pmt_dir_south": None,
							"pmt_dir_east": None}

		console_controls = {"_echo": self._io_console_echo,
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
								"pause": None,
								"pmt_back": None,
								"pmt_dir_north": None,
								"pmt_dir_west": None,
								"pmt_dir_south": None,
								"pmt_dir_east": None}

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
								"pause": None,
								"pmt_back": None,
								"pmt_dir_north": None,
								"pmt_dir_west": None,
								"pmt_dir_south": None,
								"pmt_dir_east": None}

		pmt_direction_controls = {"_echo": None,
							"coag_back": None,
							"coag_next": None,
							"coag_prev": None,
							"coag_select": None,
							"console_submit": None,
							"console_input": None,
							"menu": None,
							"move_north": None,
							"move_west": None,
							"move_south": None,
							"move_east": None,
							"pause": self._io_pause,
							"pmt_back": self._io_pmt_back,
							"pmt_dir_north": self._io_pmt_dir_north,
							"pmt_dir_west": self._io_pmt_dir_west,
							"pmt_dir_south": self._io_pmt_dir_south,
							"pmt_dir_east": self._io_pmt_dir_east}

		# The controls for the map view
		if self._state.index_stack[-1][0] == VIEW_MAP:

			# You're interacting with the map
			if self._state.index_stack[-1][2] == FOCUS_MAP:

				self._controls = map_controls

			# You're interacting with the conosle
			elif self._state.index_stack[-1][2] == FOCUS_CONSOLE:

				self._controls = console_controls

		# The controls for DC view
		elif  self._state.index_stack[-1][0] == VIEW_DC:

			self._controls = coagulate_controls

		# The controls for pause view
		elif self._state.index_stack[-1][0] == VIEW_PAUSE:

			self._controls = coagulate_controls

		# The controls for direction prompt view
		elif self._state.index_stack[-1][0] == VIEW_PROMPT_DIR:

			self._controls = pmt_direction_controls

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

	def _io_pmt_back(self):
		"""Go back a prompt."""

		self._prompt_back()

	def _io_pmt_dir_north(self):
		"""Give the direction north to the prompting."""

		self._mod_prompt_input(DIR_NORTH)

	def _io_pmt_dir_west(self):
		"""Give the direction west to the prompting."""

		self._mod_prompt_input(DIR_WEST)

	def _io_pmt_dir_south(self):
		"""Give the direction south to the prompting."""

		self._mod_prompt_input(DIR_SOUTH)

	def _io_pmt_dir_east(self):
		"""Give the direction east to the prompting."""

		self._mod_prompt_input(DIR_EAST)

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

	def _mod_prompt_input(self, info):
		"""Input something into the prompt space's args and go to the next prompt."""

		# Get promptspace
		promptspace = self._state.index_stack[-1][1]

		# Add the input to the args
		promptspace["args"].append(info)

		try: 

			next_prompt = promptspace["prompts"][len(promptspace["args"])]

			# Start the next callable prompt
			if callable(next_prompt):

				next_prompt(self, copy.copy(promptspace))

			else:

				self._mod_prompt_input(next_prompt)

		except IndexError: 

			# There's nothing to prompt, so just execute the prompt ending
			self._mod_index_pop()
			promptspace["pend"](*promptspace["args"])

	def _mod_set_next_turn(self, mob, action):
		"""Set the next turn of the mob."""

		mob.next_turn = action
	
	def _pend_co_do_action(self, *args):
		"""Finish Game.co_do_action after all information has been prompted."""

		# Set the action to what's in focus
		player = self._state.index_stack[-1][1]
		action = [self._deref_index(self._state.index_stack[-1][:-1])]
		action.extend(args)
		self._mod_set_next_turn(player, action)

		# Go back to the map view
		self._mod_index_pop()

	def _prompt_start(self, pend_func, prompts, allow_exit=False):
		"""Begin prompting and make the prompt space."""

		# Make the promptspace
		promptspace = {	"pend": pend_func,
						"args": [],
						"prompts": prompts,
						"allow_exit": allow_exit}

		# Store it in the index so that the length is constant
		self._mod_index_push([VIEW_PROMPT_NULL, promptspace])

		# Check if there's anything to prompt
		try: 

			next_prompt = promptspace["prompts"][0]

			# Start the next callable prompt
			if callable(next_prompt):

				next_prompt(self, copy.copy(promptspace))

			else:

				self._mod_prompt_input(next_prompt)

		except IndexError: 

			# There's nothing to prompt, so just execute the prompt ending
			self._mod_index_pop()
			promptspace["pend"](*promptspace["args"])

	def _prompt_back(self):
		"""Go back to the previous prompt."""

		# Get promptspace
		promptspace = self._state.index_stack[-1][1]

		# Check if there's anything to go back to 
		try: 

			promptspace["args"].pop()
			prev_prompt = promptspace["prompts"][len(promptspace["args"])]

			# Start the previous callable prompt
			if callable(prev_prompt):

				prev_prompt(self, copy.copy(promptspace))

			else:

				self._prompt_back()

		except IndexError: 

			# There's nothing to left to go back to
			if promptspace["allow_exit"]:

				self._mod_index_pop()

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

# Functions
def _path_from_id(id_):
	"""Get a path to a file based on its ID."""

	return os.path.join(os.path.dirname(__file__), *id_.split(':'))