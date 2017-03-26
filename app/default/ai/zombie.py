import random

from ...ai_super import AI

DIR_ACTION = {	(0, 0): "default:action:wait",
				(0, -1): "default:action:move_north",
				(1, -1): "default:action:move_northeast",
				(1, 0): "default:action:move_east",
				(1, 1): "default:action:move_southeast",
				(0, 1): "default:action:move_south",
				(-1, 1): "default:action:move_southwest",
				(-1, 0): "default:action:move_west",
				(-1, -1): "default:action:move_northwest"}

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
					entity = tile.layers[mob.coords[2]][mob.permeability]

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

		if DIR_ACTION[direction] == "default:action:wait" and found_flag:

			for action in mob.actions:
				if action.id == "default:action:zombie_bite":

					return [action]

		for action in mob.actions:
			if action.id == DIR_ACTION[direction]:

				return [action]
		# *** DEBUG ***
