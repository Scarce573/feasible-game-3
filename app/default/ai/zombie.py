import random

from ...ai_super import AI

DIR_NORTH = 0
DIR_NORTHEAST = 1
DIR_EAST = 2
DIR_SOUTHEAST = 3
DIR_SOUTH = 4
DIR_SOUTHWEST = 5
DIR_WEST = 6
DIR_NORTHWEST = 7

DIR_ACTION = {	(0, -1): DIR_NORTH,
				(1, -1): DIR_NORTHEAST,
				(1, 0): DIR_EAST,
				(1, 1): DIR_SOUTHEAST,
				(0, 1): DIR_SOUTH,
				(-1, 1): DIR_SOUTHWEST,
				(-1, 0): DIR_WEST,
				(-1, -1): DIR_NORTHWEST}

class DefAI(AI):
	"""
	The AI for a basic zombie

	DefAI.get_next_turn(map_, mob)

	Also includes some members froma AI 
	"""

	@staticmethod
	def get_next_turn(map_, mob):
		"""Get the next action of the mob."""

		# *** DEBUG ***
		view_distance = 3	# Note that this is two-sided
		offset = (0, 0)
		found_flag = False

		for x_dif in range(-view_distance, view_distance):
			for y_dif in range(-view_distance, view_distance):

				try:
					tile = map_.grid[mob.coords[0] + x_dif][mob.coords[1] + y_dif]
					entity = tile.layers[mob.coords[2]][int(mob.quanta["default:quanta:_permeability"])]

					if entity.id == "default:mob:player":

						offset = (x_dif, y_dif)
						found_flag = True

				except IndexError: continue
				except KeyError: continue

		try:

			direction_x = offset[0] / abs(offset[0])

		except ZeroDivisionError:

			direction_x = 0

		try:

			direction_y = offset[1] / abs(offset[1])

		except ZeroDivisionError:

			direction_y = 0

		direction = (direction_x, direction_y)

		if direction == (0, 0) and found_flag:

			return [mob.actions["default:action:zombie_bite"]]

		elif direction == (0, 0) and not found_flag:

			return [mob.actions["default:action:wait"]]

		else:

			return [mob.actions["default:action:walk"], DIR_ACTION[direction]]
		# *** DEBUG ***