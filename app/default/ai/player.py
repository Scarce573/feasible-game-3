from ... import ai_super

DIR_NORTH = 0
DIR_NORTHEAST = 1
DIR_EAST = 2
DIR_SOUTHEAST = 3
DIR_SOUTH = 4
DIR_SOUTHWEST = 5
DIR_WEST = 6
DIR_NORTHWEST = 7

DIR_ACTION = {	DIR_NORTH: "default:action:move_north",
		DIR_NORTHEAST: "default:action:move_northeast",
		DIR_EAST: "default:action:move_east",
		DIR_SOUTHEAST: "default:action:move_southeast",
		DIR_SOUTH: "default:action:move_south",
		DIR_SOUTHWEST: "default:action:move_southwest",
		DIR_WEST: "default:action:move_west",
		DIR_NORTHWEST: "default:action:move_northwest"}

class DefAI(ai_super.AI):
	"""
	The AI for a user-controlled mob

	AI.get_move(mob, direction)

	Also includes some members from AI 
	"""

	@staticmethod
	def get_move(mob, direction):

		if DIR_ACTION[direction] in mob.get_actions():

			return DIR_ACTION[direction]
