import numpy as np

from manimlib import Rotation
from manimlib.constants import *



# Step constants that can be used for building dynamical systems
# (they represent a dt, or time step)
UHD_TIME_DELTA = 0.00666666666666666
HD_TIME_DELTA =  0.01666666666666572
SD_TIME_DELTA  = 0.06666666666666666
LOW_QUALITY_TIME_DELTA  = 0.15
DEFAULT_TIME_DELTA = HD_TIME_DELTA


"""Snapshot-related constants"""

# Default time domain when building dynamical system snapshots
# without a specified domain
DS_SNAPSHOT_DEFAULT_TIME_DOMAIN = [-10, 10]

# Distance (horizontal or vertical) between initial positions in a phase plane
# For example, a step of 1 on an axis with range [0, 2] would place points on
# x=0, x=1 and x=2.
DS_PHASE_PLANE_DEFAULT_STEP = 1


"""Velocity color-coding-related constants"""

# Number of iterations of the system to calculate when color coding
# a system from its trace
DS_TRACE_COLOR_CODING_N_OF_ITERATIONS = 200

# Number of iterations of the system to calculate when color coding
# a system from its trace
DS_PLANE_COLOR_CODING_VALUES_RANGE = 10

# Number of intermediate colors between the given 'slow' and 'medium', and
# 'medium' and 'fast' colors
DS_COLOR_CODING_VARIETY = 20

# Amount by which to scale the calculated color coding limit
DS_COLOR_CODING_SCALE_FACTOR = 0.93


"""Style-related constants"""

SOME_VELOCITY_COLORS = {
    'blue': ['#8ecae6', '#219ebc', '#045a85'],  # blues
    'green1': ['#84a98c', '#52796f', '#354f52'],  # greens - alternative last: '#354f52' / alt first: '#cad2c5'
    'salmon_dont_use': ['#ffcdb2', '#ffb4a2', '#e5989b'],  # oranges/salmon
    'teal1': ['#bdc7b7', '#69a297', '#487481'],  # teals?
    'magenta2': ['#dca3ae', '#d28897', '#a35c68'], 
    'purple1': ['#a189a9', '#7c6783', '#56445d'],  # purple ish
    'purple2': ['#b196cc', '#916bb7', '#69458d'],  # purple ish v2 - chen lee here
    'green2': ['#30bb7d', '#269563', '#12462f'],  # greens
    'teal2': ['#a3c9a8', '#69a297', '#50808e'],  # teals?
    'yellow_red_pastel': ['#dbf76a', '#f7cd6a', '#f7866a'],
    # 'yellow_red_pastel': ['#9fcf89', '#f7cd6a', '#f7866a']
    'blue2': ['#64b6dd', '#219ebc', '#023047'],
    'terracota': ['#9a8c98', '#4a4e69', '#414170'],
    'teal3': ['#00a896', '#028090', '#05668d'],
    'green3_very_dark': ['#52796f', '#354f52', '#2f3e46'],
    'green3_very_dark2': ['#72a094', '#4a6f72', '#374851'],
    'green4_similar_to_teal1': ['#84a98c', '#52796f', '#354f52'],
    'dark_purple': ['#808c79', '#958c9c', '#423c45',],  # '#4d4651'],
    'orange_red': ['#d1a99d', '#ae7251', '#9c443c'],
    'sea_blue': ['#9fb5d0' , '#5b86a9', '#334b68']
}


"""ExpandedThreeDScene-related constants"""

# Buff to prevent superposition between traces (which darkens colors and looks ugly)
EXP_SCENE_DEFAULT_TRACE_OVERLAP_BUFF = 0.0225

# Default rate of camera rotation
EXP_SCENE_DEFAULT_CAMERA_ROTATION_RATE = 0.00375 # 0.003

# Default initial rotation of the camera
EXP_SCENE_DEFAULT_CAMERA_ROTATION = Rotation.from_rotvec(
    np.pi/4 * np.array([0, 0, 1])
) * Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))

# Default step when calculating a system's initial positions
EXP_SCENE_DEFAULT_STEP = 0.5

# Default range limit (both negative and positive) when calculating a system's initial positions
EXP_SCENE_DEFAULT_RANGE_LIMIT = 1

# Default maximum velocity when color-coding a system
EXP_SCENE_DEFAULT_MAX_VELOCITY = 10
