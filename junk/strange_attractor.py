from manimlib import *
import sys
# Don't know why but ManimGL doesn't add current working directory as part of the PATH.
# Doing this so I can import dynamical_systems.
sys.path.append('/Users/matiaspalumbo/Documents/Manim stuff/dynamical_systems_module_and_video')
from dynamical_systems.dynamical_systems.dynamical_systems_new_source_code import *
import numpy as np
import math
from colour import Color

# SOME_VELOCITY_COLORS = {
#     'blue': ['#8ecae6', '#219ebc', '#045a85'], # blues
#     'green1': ['#84a98c', '#52796f', '#354f52'], # greens - alternative last: '#354f52' / alt first: '#cad2c5'
#     'salmon_dont_use': ['#ffcdb2', '#ffb4a2', '#e5989b'], # oranges/salmon
#     'teal1': ['#bdc7b7', '#69a297', '#487481'], # teals?
#     'magenta': ['#dca2ad', '#ce7d8d', '#b9465c'], # 
#     'purple1': ['#a189a9', '#7c6783', '#56445d'], # purple ish
#     'purple2': ['#b196cc', '#916bb7', '#69458d'], # purple ish v2 - chen lee here
#     'green2': ['#30bb7d', '#269563', '#12462f'],#, # greens
#     'teal2': ['#a3c9a8', '#69a297', '#50808e'], # teals?
#     'yellow_red_pastel': ['#dbf76a', '#f7cd6a', '#f7866a'],
#     # 'yellow_red_pastel': ['#9fcf89', '#f7cd6a', '#f7866a']
#     'blue2': ['#64b6dd', '#219ebc', '#023047'],
#     'terracota': ['#9a8c98', '#4a4e69', '#414170'],
#     'teal3': ['#00a896', '#028090', '#05668d'],
#     'green3_very_dark': ['#52796f', '#354f52', '#2f3e46'],
#     'green3_very_dark2': ['#5c887d', '#3d5b5e', '#2f3e46'],
#     'green4_similar_to_teal1': ['#84a98c', '#52796f', '#354f52'],
#     'dark_purple': ['#808c79', '#958c9c', '#4d4651'],
# }


class StrangeAttractor:
    def __init__(self, name, dx, dy, dz, width, speed_rate, color_palette, max_velocity, preferred_scale_factor, init_pos, center):
        self.name = name
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.width= width
        self.speed_rate= speed_rate
        self.color_palette = color_palette
        self.max_velocity = max_velocity
        self.preferred_scale_factor = preferred_scale_factor
        self.init_pos = init_pos
        self.center = np.array(center)

    def scaled(self, scale_factor):
        """Returns a scaled system. Larger scale_factor results in larger system."""

        return [
            lambda x, y, z: scale_factor * self.dx(x/scale_factor, y/scale_factor, z/scale_factor),
            lambda x, y, z: scale_factor * self.dy(x/scale_factor, y/scale_factor, z/scale_factor),
            lambda x, y, z: scale_factor * self.dz(x/scale_factor, y/scale_factor, z/scale_factor)
        ]
    

LORENTZ_ATTRACTOR = StrangeAttractor(
    name='lorentz',
    dx=lambda x,y,z: 10 * (y - x),
    dy=lambda x,y,z: 28 * x - y - x * z,
    dz=lambda x,y,z: x * y - 8/3 * z,
    width=2.5,
    speed_rate=0.325,
    color_palette=SOME_VELOCITY_COLORS['teal1'],
    max_velocity=20,
    preferred_scale_factor=0.125,
    init_pos=(0.0, -1.0, 1.5),
    center=[0, 0, 3.5],
)
HALVORSEN_ATTRACTOR = StrangeAttractor(
    name='halvorsen',
    dx=lambda x,y,z: - 1.89 * x - 4 * y - 4 * z - y**2,
    dy=lambda x,y,z: - 1.89 * y - 4 * z - 4 * x - z**2,
    dz=lambda x,y,z: - 1.89 * z - 4 * x - 4 * y - x**2,
    width=2,
    speed_rate=0.22,
    color_palette=SOME_VELOCITY_COLORS['magenta'],
    max_velocity=18,
    preferred_scale_factor=0.28,
    init_pos=(0.9699999999999998, 0.9699999999999998, -0.88),
    # center=[-0.71474554, -0.71334269, -0.79970691],
    center=[-0.60324335, -0.82967388, -0.90370904],
)
CHEN_LEE_ATTRACTOR = StrangeAttractor(
    name='chen_lee',
    dx=lambda x,y,z: 5 * x - y * z,
    dy=lambda x,y,z: -10 * y + x * z,
    dz=lambda x,y,z: -0.38 * z + (x * y / 3),
    width=1.8,
    speed_rate=0.4,
    color_palette=SOME_VELOCITY_COLORS['purple2'],
    max_velocity=10,
    preferred_scale_factor=0.15,
    init_pos=(0.5, 0.5, 0.5),
    # center=[-0.71474554, -0.71334269, -0.79970691],
    center=[0, 0, 0],
)
# AIZAWA_ATTRACTOR = StrangeAttractor()
# THOMAS_ATTRACTOR = StrangeAttractor()




class AttractorColorTesting(ThreeDScene):
    ATTRACTORS = [LORENTZ_ATTRACTOR, HALVORSEN_ATTRACTOR, CHEN_LEE_ATTRACTOR]#, AIZAWA_ATTRACTOR, THOMAS_ATTRACTOR]
    # ATTRACTORS = [HALVORSEN_ATTRACTOR]
    def construct(self):
        def get_dt(dt, offset=0):
            return 0.1 + math.cos(dt + offset)
        self.camera.frame.set_orientation(
            Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1])) * Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
        )

        # attractor_systems = []
        color = SOME_VELOCITY_COLORS['terracota']
        for attractor in self.ATTRACTORS:
            funcs = attractor.scaled(attractor.preferred_scale_factor)
            system = DynamicalSystemSnapshot(
                init_pos=attractor.init_pos,
                scene=self,
                dx=funcs[0],
                dy=funcs[1],
                dz=funcs[2],
                time_domain=[0, 100],
                point_radius=0.015,
                show_point=False,
                width=attractor.width,
                speed_rate=attractor.speed_rate,
                color_code_velocity="manual",
                velocity_colors=[
                    (color[0], 0),
                    (color[1], 0),
                    (color[2], attractor.max_velocity)
                ],
            )
            # print(attractor.center)
            system.add_to_scene()
            self.camera.frame.add_updater(
                lambda camFrame, dt: camFrame.rotate(
                    angle=0.002,
                    axis=get_dt(dt)*OUT + get_dt(dt, PI/2)*UP + get_dt(dt, PI)*RIGHT,
                    about_point=attractor.center
                )
            )
            self.wait(10)
            system.remove_from_scene()


        # for attractor in attractor_systems:
        #     attractor.add_to_scene()
            # attractor.point_and_trace.trace = attractor.point_and_trace.trace.scale(.1)
            # print(attractor.trace.submobjects)
            # attractor.trace.scale(.1)
            # self.camera.frame.scale(.5).to_corner(DL)
        # attractor_systems.add_to_scene()
