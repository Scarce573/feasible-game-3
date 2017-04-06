from ...ai_super import AI

class DefAI(AI):
	"""
	The AI for a user-controlled mob

	DefAI.get_move(mob, direction)

	Also includes some members from AI 
	"""

	@staticmethod
	def get_move(mob, direction):

		#if DIR_ACTION[direction] in mob._find_actions():

		return [mob.actions["default:action:walk"], direction]
