# Andrew Bogdan
# Feasilbe Game 3
# coag_funcs.py
"""
	This file contains all and only functions which can be called directly from coagulates and prompts for information. This serves as a way to restrict jank from modifying the state file.
"""

# Imports
from constants import *

# Functions
def co_do_action(self, *args):
	"""Perform the clicked action next turn."""

	self._prompt_start(self._pend_co_do_action, list(args), allow_exit=True)

def co_pass_(self):
	"""Do nothing."""

	pass

def co_quit(self):
	"""Quit the game by way of the menu."""

	self._stop()

def co_resume(self):
	"""Resume the game."""

	self._mod_index_pop()


def pmt_direction(self, promptspace):
	"""Prompt for directional input when the map is visible."""

	self._mod_index_pop()
	self._mod_index_push([VIEW_PROMPT_DIR, promptspace, self._state.index_stack[0][1]])