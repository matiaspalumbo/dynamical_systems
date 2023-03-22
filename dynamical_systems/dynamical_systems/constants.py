from manimlib import Rotation
from manimlib.constants import *
from dynamical_systems.abstract_dynamical_system import DynamicalSystemStyle
import numpy as np



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

# Number of intermediate colors between the given 'slow' and 'medium', and
# 'medium' and 'fast' colors
DS_COLOR_CODING_VARIETY = 20

# Amount by which to scale the calculated color coding limit
DS_COLOR_CODING_SCALE_FACTOR = 0.93


"""Style-related constants"""

BASE_STYLE = DynamicalSystemStyle(
    speed_rate = 1, # Larger speed rate results in less smoothness
    color = '#3e99a0', # Main system trace color
    width = 3.2, # Main system trace width
    stroke_opacity = 1, # Main system stroke opacity
    point_radius = 0.05,
    point_color=WHITE,
    local_section_perp_vector_color = GREEN,
    local_section_vector_color = GREY,
    local_section_vec_freq = 4,
    flow_box_perp_vector_color = PURPLE_E,
    flow_box_trace_color = PURPLE_A,
    flow_box_trace_width = 3.2,
    flow_box_solution_time_domain = [-0.5, 0.5],
    velocity_colors= [(GREEN, 0), (YELLOW, 5), (RED, 10)], # Each number represents at least how big the derivative must be to color the curve that way
    trace_fadeout_decrease_factor = 0.05,
    amount_to_not_fade_out_trace_before = 5,
    line_trace_overlap_buff=0.02,
    max_number_of_trace_lines=500,
    # [int] How many times to split dt in a single frame to add more steps to the approximation.
    # Increase to add detail and preserve speed rate, or if there is a large variation in speed in the system.
    precision_multiplier_if_trace_too_rough=1,
)

PHASE_PLANE_STYLE = DynamicalSystemStyle.from_existing_style(
    BASE_STYLE,
    point_radius=0.035,
    width=2.8,
    stroke_opacity=0.65
)

SOME_VELOCITY_COLORS = {
    'blue': ['#8ecae6', '#219ebc', '#045a85'], # blues
    'green1': ['#84a98c', '#52796f', '#354f52'], # greens - alternative last: '#354f52' / alt first: '#cad2c5'
    'salmon_dont_use': ['#ffcdb2', '#ffb4a2', '#e5989b'], # oranges/salmon
    'teal1': ['#bdc7b7', '#69a297', '#487481'], # teals?
    'magenta': ['#dca2ad', '#ce7d8d', '#b9465c'], # 
    'purple1': ['#a189a9', '#7c6783', '#56445d'], # purple ish
    'purple2': ['#b196cc', '#916bb7', '#69458d'], # purple ish v2 - chen lee here
    'green2': ['#30bb7d', '#269563', '#12462f'],#, # greens
    'teal2': ['#a3c9a8', '#69a297', '#50808e'], # teals?
    'yellow_red_pastel': ['#dbf76a', '#f7cd6a', '#f7866a'],
    # 'yellow_red_pastel': ['#9fcf89', '#f7cd6a', '#f7866a']
    'blue2': ['#64b6dd', '#219ebc', '#023047'],
    'terracota': ['#9a8c98', '#4a4e69', '#414170'],
    'teal3': ['#00a896', '#028090', '#05668d'],
    'green3_very_dark': ['#52796f', '#354f52', '#2f3e46'],
    'green3_very_dark2': ['#72a094', '#4a6f72', '#374851'],
    'green4_similar_to_teal1': ['#84a98c', '#52796f', '#354f52'],
    'dark_purple': ['#808c79', '#958c9c', '#423c45',]# '#4d4651'],
}


"""ExpandedThreeDScene-related constants"""

# Buff to prevent superposition between traces (which darkens colors and looks ugly)
EXP_3D_SCENE_DEFAULT_TRACE_OVERLAP_BUFF = 0.0225

# Default rate of camera rotation
EXP_3D_SCENE_DEFAULT_CAMERA_ROTATION_RATE = 0.00375 # 0.003

# Default initial rotation of the camera
EXP_3D_SCENE_DEFAULT_CAMERA_ROTATION = Rotation.from_rotvec(
    np.pi/4 * np.array([0, 0, 1])
) * Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))

# Default step when calculating a system's initial positions
EXP_3D_SCENE_DEFAULT_STEP = 0.5

# Default range limit (both negative and positive) when calculating a system's initial positions
EXP_3D_SCENE_DEFAULT_RANGE_LIMIT = 1

# Default maximum velocity when color-coding a system
EXP_3D_SCENE_DEFAULT_MAX_VELOCITY = 10
