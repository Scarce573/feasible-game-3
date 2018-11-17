# Andrew Bogdan
# Feasilbe Game 3
# constants.py
"""
	A bunch of necessary constants
"""


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