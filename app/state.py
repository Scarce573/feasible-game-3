# Andrew Bogdan
# Feasilbe Game 3
# state.py
"""
	Holds the game state: no modifying functions.
"""

# Imports
import copy
import json

import coag_funcs
from constants import *

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

VIEW_PROMPT_NULL = 10
VIEW_PROMPT_DIR = 11

# Classes
class State(object):
	"""
	The class which contains all the in-game information necessary to take a snapshot

	State.__init__(self, map_, index_stack, message_log=[])
	State.__repr__(self)
	State.__str__(self)
	State.to_dict(self)

	State.index_stack
	State.map
	State.message_log
	State.pause_coag
	"""

	def __init__(self, map_, index_stack, message_log=[]):
		"""
		Initialize the State.
		"""

		self.map = load_if_dict(map_)
		self.message_log = message_log

		# Construct index
		self.index_stack = index_stack

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

		self.pause_coag = Coagulate(name="Paused",
									tree=[	Coagulate(name="Quit", method=[coag_funcs.co_quit]),
											Coagulate(name="Resume", method=[coag_funcs.co_resume])],
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
		state["map_"] = self.map.to_dict()
		state["message_log"] = self.message_log

		# Return state
		return state

class Map(object):
	"""
	The class which contains a grid of tiles

	Map.__init__(self, grid=[])
	Map.__repr__(self)
	Map.__str__(self)
	Map.get_mobs(self)
	Map.to_dict(self)
	Map.yield_mobs(self)

	Map.grid
	Map.size
	"""

	def __getattr__(self, attr):
		"""Get an attribute, but do a special behavior with size."""

		if attr == "size":
			if len(self.grid):

				return (len(self.grid), len(self.grid[0]))

		else:

			super(Action, self).__getattr__(attr)

	def __init__(self, grid=[]):
		"""Initialize the Map."""

		# Construct grid
		self.grid = []

		for x_val in range(len(grid)):

			saved_col = grid[x_val]
			col = []

			for y_val in range(len(saved_col)):

				saved_tile = grid[x_val][y_val]
				col.append(load_if_dict(saved_tile, coords=[x_val, y_val]))

			self.grid.append(col)

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

	Tile.__init__(self, coords=(-1, -1), layers=[])
	Tile.__repr__(self)
	Tile.__str__(self)
	Tile.get_mobs(self)
	Tile.to_dict(self)

	Tile.coords
	Tile.layers
	"""

	def __init__(self, coords=(-1, -1), layers=[]):
		"""Initialize the Tile."""

		# Construct layers
		self.layers = []

		for saved_layer_dict in layers:

			layer = {}

			for perm_str in saved_layer_dict:

				permeability = int(perm_str)

				entity_coords = copy.copy(coords)
				entity_coords.append(permeability)

				layer[permeability] = load_if_dict(saved_layer_dict[perm_str], coords=entity_coords)

			self.layers.append(layer)

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
	Entity.__init__(self, inventory, knowledge, status, coords=(-1, -1, -1), id_="")
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

	def __init__(self, inventory, knowledge, status, coords=(-1, -1, -1), id_=""):
		"""Initialize the Entity."""

		self.coords = coords
		self.id = id_
		self.inventory = load_if_dict(inventory)
		self.knowledge = load_if_dict(knowledge)
		self.status = load_if_dict(status)

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
		state["id_"] = self.id
		state["inventory"] = self.inventory.to_dict()
		state["knowledge"] = self.knowledge.to_dict()
		state["status"] = self.status.to_dict()

		# Return state
		return state

class NonMob(Entity):
	"""
	An entity wihout an AI

	NonMob.__init__(self, **argsd)
	NonMob.to_dict(self)

	Also includes some member variables from Entity
	"""

	def __init__(self, **argsd):
		"""Initialize the NonMob."""

		super(NonMob, self).__init__(**argsd)

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
	Mob.__init__(self, ai="", next_turn=None, **argsd)
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

	def __init__(self, ai="", next_turn=None, **argsd):
		"""Initialize the Mob."""

		super(Mob, self).__init__(**argsd)

		self.ai = ai
		self.next_turn = next_turn

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
	Coagulate.__init__(self, name="", tree=[], method=[coag_funcs.co_pass_], is_root=False)
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

	def __init__(self, name="", tree=[], method=[coag_funcs.co_pass_], is_root=False):
		"""Initialize the Coagulate."""

		self.is_root = is_root
		self.name = name

		# Construct tree
		self._tree = []

		for coag in tree:

			self._tree.append(load_if_dict(coag))

		# Construct method
		self.method = []

		for arg in method:
			if type(arg) == str:
				if arg.find('$') != -1:

					self.method.append(coag_funcs.__dict__[arg[arg.index('$') + 1:]])

			else:

				self.method.append(arg)
			

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
	
	__init__(self, id_="", **argsd)
	Differentia.to_dict(self)

	Differentia.id

	Also includes some member variables from Coagulate.
	"""

	def __init__(self, id_="", **argsd):
		"""Initialize the Differentia."""

		# Issue: This is deleting the inate quanta/lita of Figments

		try: del argsd["method"]
		except KeyError: pass

		super(Differentia, self).__init__(method=[coag_funcs.co_pass_], **argsd)

		self.id = id_

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Differentia."""

		state = super(Differentia, self).to_dict()

		# Construct state
		state["_type"] = "Differentia"
		state["id_"] = self.id

		# Return state
		return state

class Figment(Differentia):
	"""
	A figment of the game, such as an item, status, or concept.

	Figment.__getattr__(self, attr)
	Figment.__init__(	self, actions=[], qualita_inate=[], qualita_inherited=[], 
						quanta_inate=[], quanta_inherited=[], **argsd)
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

	def __init__(	self, actions=[], qualita_inate=None, qualita_inherited=[], 
					quanta_inate=None, quanta_inherited=[], **argsd):
		"""
		Initialze the Figment.

		Both quanta_inate and qualita_inate need to be defined for it do override tree.
		"""

		super(Figment, self).__init__(**argsd)
			
		# Construct inherit lists
		self.actions = []
		self.qualita_inherited = []
		self.quanta_inherited = []

		for saved_action in actions:

			action = []
			action.append(load_if_dict(saved_action[0]))
			action.extend(saved_action[1:])
			self.actions.append(action)

		for saved_qualita in qualita_inherited:

			qualita = []
			qualita.append(load_if_dict(saved_qualita[0]))
			qualita.extend(saved_qualita[1:])
			self.qualita_inherited.append(qualita)

		for saved_quanta in quanta_inherited:

			quanta = []
			quanta.append(load_if_dict(saved_quanta[0]))
			quanta.extend(saved_quanta[1:])
			self.quanta_inherited.append(quanta)
		
		# Override the data in tree
		if qualita_inate is not None and quanta_inate is not None:

			self._tree[0] = (Coagulate(	name="Qualita",
										tree=qualita_inate,
										is_root=False))

			self._tree[1] =	(Coagulate(	name="Quanta",
										tree=quanta_inate,
										is_root=False))

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

	Item.__init__(self, **argsd)
	Item.to_dict(self)
	"""

	def __init__(self, **argsd):
		"""Initialze the Item."""

		super(Item, self).__init__(**argsd)

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

	Status.__init__(self, **argsd)
	Status.to_dict(self)
	"""

	def __init__(self, **argsd):
		"""Initialze the Status."""

		super(Status, self).__init__(**argsd)

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

	Concept.__init__(self, **argsd)
	Concept.to_dict(self)
	"""

	def __init__(self, **argsd):
		"""Initialze the Concept."""

		super(Concept, self).__init__(**argsd)

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

	Characteristic.__init__(self, value=None, **argsd)
	Characteristic.to_dict(self)

	Characteristic._value
	"""

	def __init__(self, value=None, **argsd):
		"""Initialze the Characteristic."""

		try: del argsd["tree"]
		except KeyError: pass

		super(Characteristic, self).__init__(tree=[], **argsd)

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

	Qualita.__init__(self, value=True, **argsd)
	Qualita.to_dict(self)
	"""

	def __init__(self, value=True, **argsd):
		"""Initialze the Qualita."""

		super(Qualita, self).__init__(value=value, **argsd)

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
	Quanta.__init__(self, value=0, **argsd)
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

	def __init__(self, value=0, **argsd):
		"""Initialze the Quanta."""

		super(Quanta, self).__init__(value=value, **argsd)

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
	Action.__init__(self, qualita=[], quanta=[], **argsd)
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

	def __init__(self, qualita=None, quanta=None, **argsd):
		"""
		Initialze the Action.

		Both quanta and qualita need to be defined for it do override tree.
		"""

		super(Action, self).__init__(**argsd)

		if qualita is not None and quanta is not None:

			self._tree.append(Coagulate(name="Qualita",
										tree=qualita,
										is_root=False))
			self._tree.append(Coagulate(name="Quanta",
										tree=quanta,
										is_root=False))

	def to_dict(self):
		"""Create a JSON-serializable dict representation of the Action."""

		state = super(Action, self).to_dict()

		# Construct state
		state["_type"] = "Action"

		# Return state
		return state

# Functions
def load_if_dict(saved_state, **argsd):
	"""
	Load an instance from a dict with the "_type" key.

	Because copy.copy is used, editing is fair game.
	"""

	# Return in case we don't have JSON
	if type(saved_state) != dict: return saved_state

	ss_copy = copy.copy(saved_state)
	type_ = ss_copy.pop("_type")
	ss_copy.update(argsd)

	return globals()[type_](**ss_copy)