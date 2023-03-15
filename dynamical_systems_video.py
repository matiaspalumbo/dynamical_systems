import sys
# Don't know why but ManimGL doesn't add current working directory as part of the PATH.
# Doing this so I can import dynamical_systems.
sys.path.append('/Users/matiaspalumbo/Documents/Manim stuff/dynamical_systems')

from manimlib import *
from dynamical_systems_new_source_code import *
from strange_attractor import *
import numpy as np
import math
from colour import Color


# SOME_VELOCITY_COLORS = [
#     ['#8ecae6', '#219ebc', '#045a85'], # blues
#     ['#84a98c', '#52796f', '#354f52'], # greens - alternative last: '#354f52' / alt first: '#cad2c5'
#     ['#ffcdb2', '#ffb4a2', '#e5989b'], # oranges/salmon
#     ['#bdc7b7', '#69a297', '#487481'], # teals?
#     ['#dca2ad', '#ce7d8d', '#b9465c'], # 
#     # ['#a189a9', '#7c6783', '#56445d'], # purple ish
#     ['#b196cc', '#916bb7', '#69458d'], # purple ish v2
#     ['#30bb7d', '#269563', '#1a6443']  # greens
#     # ['#a3c9a8', '#69a297', '#50808e'], # teals?
# ]
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
DEFAULT_TRACE_OVERLAP_BUFF = 0.0225
CAMERA_ROTATION_RATE = 0.00375 # 0.003
CAMERA_ROTATION = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1])) * Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
STEP = 0.5
RANGE_LIMIT = 1
MAX_VELOCITY = 10


class ExpandedThreeDScene(ThreeDScene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def set_up_camera(self, rate=CAMERA_ROTATION_RATE, rotation=CAMERA_ROTATION, rotation_center=ORIGIN):

        def get_dt(dt, offset=0):
            return 0.1 + math.cos(dt + offset)
        
        # Set up rotation
        self.camera.frame.set_orientation(rotation)

        # Set up rotation center - in most cases, average center of the system
        self.camera.frame.move_to(rotation_center)

        # Continuously rotate camera
        self.camera.frame.add_updater(
            lambda camFrame, dt: camFrame.rotate(
                angle=rate,
                axis=get_dt(dt)*OUT + get_dt(dt, PI/2)*UP + get_dt(dt, PI)*RIGHT,
                about_point=rotation_center,
            )
        )
    
    def set_up_axes(self):
        axes_config = dict(tip_length=0.2, tip_width=0.2, fill_opacity=0.3)
        axes_length = 50
        axes = ThreeDAxes(
            x_range=[-axes_length, axes_length],
            y_range=[-axes_length, axes_length],
            z_range=[-axes_length, axes_length],
            axis_config=axes_config,
            z_axis_config=axes_config
        )
        self.add(axes)
        return axes

    def get_initial_positions(
            self,
            ranges=[[-RANGE_LIMIT, RANGE_LIMIT, STEP]]*3,
            remove_z_axis=False,
            remove_origin=False, 
            return_position=0):
        initial_positions = set([
            (x, y, z) for x in np.arange(ranges[Coords.X][0], ranges[Coords.X][1], ranges[Coords.X][2])
            for y in np.arange(ranges[Coords.Y][0], ranges[Coords.Y][1], ranges[Coords.Y][2])
            for z in np.arange(ranges[Coords.Z][0], ranges[Coords.Z][1], ranges[Coords.Z][2])
        ])
        if return_position:
            return list(initial_positions)[return_position:return_position+1]
        if remove_z_axis:
            return initial_positions - set([pos for pos in initial_positions if pos[0] == 0 and pos[1] == 0])
        elif remove_origin:
            return initial_positions - {(0,0,0)}
        else:
            return initial_positions
        
    def get_velocity_colors(self, color_index: str='blue', max_velocity=MAX_VELOCITY, slow_to_med_weight=0):
        return [
            (SOME_VELOCITY_COLORS[color_index][0], slow_to_med_weight),
            (SOME_VELOCITY_COLORS[color_index][1], 0),
            (SOME_VELOCITY_COLORS[color_index][2], max_velocity)
        ] # The first and second number don't do anything for now



class HalvorsenAttractorScene(ExpandedThreeDScene):
    def construct(self):
        a = 1.89
        alpha = 0.28 # escala el sistema
        halvorsen_x = lambda x,y,z: - a * x - 4 * y - 4 * z - alpha*(y/alpha)**2
        halvorsen_y = lambda x,y,z: - a * y - 4 * z - 4 * x - alpha*(z/alpha)**2
        halvorsen_z = lambda x,y,z: - a * z - 4 * x - 4 * y - alpha*(x/alpha)**2

        # self.set_up_camera(
        #     rate=0.003,
        #     # rotation_center=np.array([-0.67922174, -0.67611461, -0.67617357])
        #     # rotation_center=np.array([-0.96069974, -1.24244918, -1.09488434])
        #     # rotation_center=np.array([-0.880977, -0.94991739, -0.98049987])
        #     # rotation_center=np.array([-0.80496794, -0.80964933, -0.81001214])
        #     rotation_center=np.array([-0.60324335, -0.82967388, -0.90370904])
        # )

        bd = 1.25
        step = 0.37 # .25 # 5
        initial_positions = self.get_initial_positions(
            ranges=[[-bd, bd - 0.1, step]]*3,  # x/y/z_range and steps
            remove_z_axis=True,  # remove all positions with x=y=0
            remove_origin=False,   # remove (0,0,0)
            return_position=False  # return a single specific position (either False/0 or an int)
        )
        initial_positions = list(initial_positions)[:1]


        base_params = dict(
            initial_positions=initial_positions,
            scene=self,
            dx=halvorsen_x,
            dy=halvorsen_y,
            dz=halvorsen_z,
        )
        style_params = dict(
            point_radius=0.015,#0.035,
            point_color=GREY_B,
            width=2,
            speed_rate=.22, #0.25  # 0.22
            # Should color each trace differently? manual/from_plane/from_trace/False
            color_code_velocity="manual",
            # Base color to build velocity gradient along with max velocity
            velocity_colors=self.get_velocity_colors(color_index='magenta', max_velocity=18),
            # Should start fading out trace after a given trace length?
            # fade_out_trace=True
        )
        advanced_style_params_for_long_trace = dict(
            trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
            amount_to_not_fade_out_trace_before=7,
            line_trace_overlap_buff=DEFAULT_TRACE_OVERLAP_BUFF,
            precision_multiplier_if_trace_too_rough=3,
        )
        # Not currently used
        advanced_style_params_for_short_trace = dict(
            # Amount by which opacity is reduced each frame if trace is being faded out
            trace_fadeout_decrease_factor=0.085, #0.05, #.025, # 0.3
            # Trace sum amount before which traces shouldn't start being faded out
            amount_to_not_fade_out_trace_before=0.5, #500, #1.25, #7.5,
            # Buff to prevent superposition between traces (darkens colors and looks ugly)
            line_trace_overlap_buff=DEFAULT_TRACE_OVERLAP_BUFF,
            # Traces to calculate at each frame (to reduce blockiness)
            precision_multiplier_if_trace_too_rough=3,
        )

        # systems = DynamicalSystemFamily(
        #     **base_params,
        #     **style_params,
        #     **advanced_style_params_for_long_trace
        # )
        
        systems = DynamicalSystemSnapshot(
            init_pos=initial_positions[0],
            scene=self,
            dx=halvorsen_x,
            dy=halvorsen_y,
            dz=halvorsen_z,
            time_domain=[0,30],
            **style_params,
            **advanced_style_params_for_long_trace
        )

        systems.add_to_scene()

        self.wait(300)



class MultipleLorentzAttractorScene(ExpandedThreeDScene):
    def construct(self):
        sigma = 10
        beta = 8/3  
        rho = 28    
        alpha = 0.125 # escala el sistema
        lorentz_x = lambda x,y,z: sigma * (y - x)
        lorentz_y = lambda x,y,z: rho * x - y - x * z / alpha
        lorentz_z = lambda x,y,z: x * y / alpha - beta * z

        self.set_up_camera(
            rate=0.00975,
            rotation_center=np.array([0, 0, 3.5])
        )

        bd = 2
        step = 0.5
        initial_positions = self.get_initial_positions(
            ranges=[
                [0, bd,step],
                [-bd/2, bd/2, step],
                [0, bd, step],
            ],  # x/y/z_range and steps
            remove_z_axis=True,  # remove all positions with x=y=0
            remove_origin=False,   # remove (0,0,0)
            return_position=False  # return a single specific position (either False/0 or an int)
        )
        print(initial_positions)

        base_params = dict(
            initial_positions=initial_positions,
            scene=self,
            dx=lorentz_x,
            dy=lorentz_y,
            dz=lorentz_z,
        )
        style_params = dict(
            point_radius=0.015,
            point_color=GREY_B,
            width=2.5, #2.3
            speed_rate=0.325,
            # Should color each trace differently? manual/from_plane/from_trace/False
            color_code_velocity="manual",
            # Base color to build velocity gradient along with max velocity
            velocity_colors=self.get_velocity_colors(color_index='teal1', max_velocity=20),
            # Should start fading out trace after a given trace length?
            fade_out_trace=True
        )
        advanced_style_params = dict(
            # Amount by which opacity is reduced each frame if trace is being faded out
            trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
            # Trace sum amount before which traces shouldn't start being faded out
            amount_to_not_fade_out_trace_before=7.5, #500, #1.25, #7.5,
            # Buff to prevent superposition between traces (darkens colors and looks ugly)
            line_trace_overlap_buff=DEFAULT_TRACE_OVERLAP_BUFF,
            # Traces to calculate at each frame (to reduce blockiness)
            precision_multiplier_if_trace_too_rough=3,
        )

        systems = DynamicalSystemFamily(
            **base_params,
            **style_params,
            **advanced_style_params
        )
        systems.add_to_scene()

        self.wait(300)



class ChenLeeAttractorScene(ExpandedThreeDScene):
    def construct(self):
        alpha = 5
        beta = -10  
        delta = -0.38    
        scale = 0.15 # escala el sistema
        chen_lee_x = lambda x,y,z: alpha * x - y * z / scale
        chen_lee_y = lambda x,y,z: beta * y + x * z / scale
        chen_lee_z = lambda x,y,z: delta * z + (x * y / 3) / scale

        # Configuramos que la cámara gire lentamente a medida que se traza el sistema
        r1 = Rotation.from_rotvec((np.pi/2 - np.pi/8) * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.set_up_camera(rate=0.006, rotation=rot)

        bdx = 1 #1 #2
        bdy = 1
        step = .5 #1/8, .5,  .25
        initial_positions = set([
            (x, y, sgn * z) for x in np.arange(0, bdx, step)
            for y in np.arange(-bdy, bdy, step)
            for z in np.arange(.75, 5.1, .5)
            for sgn in [-1, 1]
        ])
        initial_positions -= set([pos for pos in initial_positions if pos[0] == 0 and pos[1] == 0])

        base_params = dict(
            initial_positions=initial_positions,
            scene=self,
            dx=chen_lee_x,
            dy=chen_lee_y,
            dz=chen_lee_z,
        )
        style_params = dict(
            point_radius=0.015, # parámetro de estilo; es el radio del punto del sistema
            point_color=GREY_B,
            width=1.8, #2.3, #2.5
            speed_rate=.4, # .5
            # Should color each trace differently? manual/from_plane/from_trace/False
            color_code_velocity="manual",
            # Base color to build velocity gradient along with max velocity
            velocity_colors=self.get_velocity_colors(color_index='purple2', max_velocity=15),
            # Should start fading out trace after a given trace length?
            fade_out_trace=True,
        )
        advanced_style_params_for_short_trace = dict(
            # Amount by which opacity is reduced each frame if trace is being faded out
            trace_fadeout_decrease_factor=0.025, #0.05, #0.3
            # Trace sum amount before which traces shouldn't start being faded out
            amount_to_not_fade_out_trace_before=3,  #2, #0.25, #500, #1.25, #7.5,
            # Buff to prevent superposition between traces (darkens colors and looks ugly)
            line_trace_overlap_buff=DEFAULT_TRACE_OVERLAP_BUFF,
            # Traces to calculate at each frame (to reduce blockiness)
            precision_multiplier_if_trace_too_rough=3,
            # Max number of trace lines to have not faded out at a given frame
            max_number_of_trace_lines=10, # 100,
        )
        # Not currently used
        advanced_style_params_for_long_trace = dict(
            # Amount by which opacity is reduced each frame if trace is being faded out
            trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
            # Trace sum amount before which traces shouldn't start being faded out
            amount_to_not_fade_out_trace_before=7.5,
            # Buff to prevent superposition between traces (darkens colors and looks ugly)
            line_trace_overlap_buff=DEFAULT_TRACE_OVERLAP_BUFF,
            # Traces to calculate at each frame (to reduce blockiness)
            precision_multiplier_if_trace_too_rough=3,
            # Max number of trace lines to have not faded out at a given frame
            max_number_of_trace_lines=10,
        )

        systems = DynamicalSystemFamily(
            **base_params,
            **style_params,
            **advanced_style_params_for_short_trace
        )

        systems.add_to_scene()
        self.wait()
        # self.wait(5)
        # self.wait(10)
        # self.wait(15)
        # self.wait(30)
        # self.wait(60)
        # self.wait(75)
        # self.wait(120)
        # self.wait(300)

        # 60s hd 60fps with one system:
        #  1:24.61 total without improvement
        #  1:24.17 total with improvement YAY 

        # 120s hd 60fps with one system:
        #  4:26.72 total without improvement
        #  4:31.65 total with improvement 

        # 5s hd 60fps with all systems:
        #  1:02.14 total without improvement
        #  1:02.74 total with improvement 


class AizawaAttractorScene(ThreeDScene):
    def set_up_camera(self, rate=0.003):
        def get_dt(dt, offset=0):
            return 0.1 + math.cos(dt + offset)

        # Set rotation
        r1 = Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.camera.frame.set_orientation(rot)
        # Set position
        about_point = np.array([0.00643597, -0.02607911,  1.5])
        self.camera.frame.move_to(about_point)
        # Continuously rotate camera
        # self.camera.frame.add_updater(
        #     lambda camFrame, dt: camFrame.rotate(
        #         angle=rate,
        #         axis=get_dt(dt)*OUT + get_dt(dt, PI/2)*UP + get_dt(dt, PI)*RIGHT,
        #         about_point=about_point,
        #     )
        # )

    def set_up_axes(self):
        axes_config = dict(tip_length=0.2, tip_width=0.2, fill_opacity=0.3)
        axes_length = 50
        axes = ThreeDAxes(
            x_range=[-axes_length, axes_length],
            y_range=[-axes_length, axes_length],
            z_range=[-axes_length, axes_length],
            axis_config=axes_config,
            z_axis_config=axes_config
        )
        self.add(axes)
        return axes

    def construct(self):
        a = 0.95
        b = 0.7
        c = 0.6
        d = 3.5
        e = 0.25
        f = 0.1
        scale = 0.55 # escala el sistema
        aizawa_x = lambda x,y,z: (z - b) * x - d * y
        aizawa_y = lambda x,y,z: d * x + (z - b) * y
        aizawa_z = lambda x,y,z: c + a * z - z**3 / 3 - (x**2 + y**2) * (1 + e * z) + f * z * x**3

        aizawa_x_scaled = lambda x,y,z: 1/scale * aizawa_x(scale*x, scale*y, scale*z)
        aizawa_y_scaled = lambda x,y,z: 1/scale * aizawa_y(scale*x, scale*y, scale*z)
        aizawa_z_scaled = lambda x,y,z: 1/scale * aizawa_z(scale*x, scale*y, scale*z)

        # Configuramos que la cámara gire lentamente a medida que se traza el sistema
        self.set_up_camera(rate=0.006)

        bdx = 1
        stepx = .25 # .25
        bdy = 1/2
        stepy = .5 # .25
        bdzneg = -2
        bdzpos = 1.1
        stepz = .5 # .25
        initial_positions = set([
            (x, y, z) for x in np.arange(-bdx, bdx, stepx)
            for y in np.arange(-bdy, bdy, stepy)
            for z in np.arange(bdzneg, bdzpos, stepz)
        ])
        initial_positions -= set([pos for pos in initial_positions if pos[0] == 0 and pos[1] == 0])
        initial_positions = [scale * np.array(pos) for pos in initial_positions]
        initial_positions = list(initial_positions)[:1]
        # initial_positions = [[scale * 0.1, scale * 0, scale * 0]]

        # initial_positions = [[0.1, 0, 0]]
        # initial_positions = [[1, 0.75, 0.85]]
        # initial_positions = list(initial_positions)[4:5]
        # initial_positions = set([(x, y, 1) for y in np.arange(-bd, bd, step)]) - {(0,0,1)}

        color_index = 'dark_purple'
        style_for_long_trace = dict(
            trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
            amount_to_not_fade_out_trace_before=7.5,
            line_trace_overlap_buff=0.0225,
            precision_multiplier_if_trace_too_rough=3,
        )
        style_for_short_trace = dict(
            trace_fadeout_decrease_factor=0.05, #0.05, #.025, # 0.3
            amount_to_not_fade_out_trace_before=1,#0.25, #500, #1.25, #7.5,
            line_trace_overlap_buff=0.0225,
            precision_multiplier_if_trace_too_rough=1,
        )

        systems = DynamicalSystemFamily(
            scene=self,
            initial_positions=initial_positions,
            dx=aizawa_x_scaled,
            dy=aizawa_y_scaled,
            dz=aizawa_z_scaled,
            color_code_velocity="manual",
            fade_out_trace=True,
            point_radius=0.015, # parámetro de estilo; es el radio del punto del sistema
            point_color=GREY_B,
            width=2.5, #2
            speed_rate=1,#.5,
            velocity_colors=[
                (SOME_VELOCITY_COLORS[color_index][0], 0),
                (SOME_VELOCITY_COLORS[color_index][1], 0),
                (SOME_VELOCITY_COLORS[color_index][2], 8.5)
            ], # The first and second number don't do anything for now
            **style_for_short_trace
        )


        # Para que este sistema se coloree bien, conviene cambiar la constante COLOR_CODING_SCALE_FACTOR
        # a algo mayor. Para el video que está en el drive, la cambié a 3 [edit: ???]
        systems.add_to_scene()
        self.wait(5)
        # self.wait(10)
        # self.wait(20)
        # self.wait(30)
        # self.wait(60)
        # self.wait(60)
        # self.wait(120)

        # 20s hd:
        #  7:16.27 total without improvement
        #  3:32.98 total with improvement YAY 


class ThomasAttractor(ExpandedThreeDScene):
    def construct(self):
        beta = 0.19
        scale = 1.5
        thomas_x = lambda x,y,z: -beta * x + math.sin(y*scale) / scale
        thomas_y = lambda x,y,z: -beta * y + math.sin(z*scale) / scale
        thomas_z = lambda x,y,z: -beta * z + math.sin(x*scale) / scale

        self.set_up_camera(rate=0.00975)

        bd = 1.5
        step = 0.6
        initial_positions = self.get_initial_positions(
            ranges=[[-bd, bd+.01, step]]*3,  # x/y/z_range and steps
            remove_z_axis=False,  # remove all positions with x=y=0
            remove_origin=False,   # remove (0,0,0)
            return_position=False  # return a single specific position (either False/0 or an int)
        )
        initial_positions = [1.4 * np.array(pos) for pos in initial_positions]
        # initial_positions = list(initial_positions)[:1]
        # initial_positions = [[.5, .5, .5]]


        base_params = dict(
            initial_positions=initial_positions,
            scene=self,
            dx=thomas_x,
            dy=thomas_y,
            dz=thomas_z,
        )
        style_params = dict(
            point_radius=0.015,
            point_color=GREY_B,
            width=2.3,
            speed_rate=1.5, # 0.325,
            # Should color each trace differently? manual/from_plane/from_trace/False
            color_code_velocity="manual",
            # Base color to build velocity gradient along with max velocity
            velocity_colors=self.get_velocity_colors(color_index='yellow_red_pastel', max_velocity=1),#, slow_to_med_weight=.65),
            # Should start fading out trace after a given trace length?
            fade_out_trace=True,
        )
        advanced_style_params = dict(
            # Amount by which opacity is reduced each frame if trace is being faded out
            trace_fadeout_decrease_factor=0.03, #0.05, #.025, # 0.3
            # Trace sum amount before which traces shouldn't start being faded out
            amount_to_not_fade_out_trace_before=1.5, #500, #1.25, #7.5,
            # Buff to prevent superposition between traces (darkens colors and looks ugly)
            line_trace_overlap_buff=DEFAULT_TRACE_OVERLAP_BUFF,
            # Traces to calculate at each frame (to reduce blockiness)
            precision_multiplier_if_trace_too_rough=1,# 3,
            # Max number of trace lines to have not faded out at a given frame
            max_number_of_trace_lines=30
        )

        systems = DynamicalSystemFamily(
            **base_params,
            **style_params,
            **advanced_style_params
        )
        systems.add_to_scene()

        # self.wait(1)
        # self.wait(3)
        # self.wait(5)
        # self.wait(15)
        # self.wait(30)
        # self.wait(60)
        # self.wait(60)


class SakaryaAttractor(ExpandedThreeDScene):
    def construct(self):
        a = 0.4
        b = 0.3
        scale = 10
        sakarya_x = lambda x,y,z: -x + y + (y * z)
        sakarya_y = lambda x,y,z: -x - y + (a * x * z)
        sakarya_z = lambda x,y,z: z - (b * x * y)

        sakarya_x_scaled = lambda x,y,z: 1/scale * sakarya_x(scale*x, scale*y, scale*z)
        sakarya_y_scaled = lambda x,y,z: 1/scale * sakarya_y(scale*x, scale*y, scale*z)
        sakarya_z_scaled = lambda x,y,z: 1/scale * sakarya_z(scale*x, scale*y, scale*z)

        self.set_up_camera(rate=0.00975)

        bd = 1.5
        step = 0.6
        initial_positions = self.get_initial_positions(
            ranges=[[-bd, bd+.01, step]]*3,  # x/y/z_range and steps
            remove_z_axis=False,  # remove all positions with x=y=0
            remove_origin=False,   # remove (0,0,0)
            return_position=False  # return a single specific position (either False/0 or an int)
        )
        # initial_positions = [1.4 * np.array(pos) for pos in initial_positions]
        # initial_positions = list(initial_positions)[:1]
        # initial_positions = [[.5, .5, .5]]


        base_params = dict(
            initial_positions=initial_positions,
            scene=self,
            dx=sakarya_x_scaled,
            dy=sakarya_y_scaled,
            dz=sakarya_z_scaled,
        )
        style_params = dict(
            point_radius=0.015,
            point_color=GREY_B,
            width=2.3,
            speed_rate=.2, #1.5 # 0.325,
            # Should color each trace differently? manual/from_plane/from_trace/False
            color_code_velocity="manual",
            # Base color to build velocity gradient along with max velocity
            velocity_colors=self.get_velocity_colors(color_index='blue2', max_velocity=10),#, slow_to_med_weight=.65),
            # Should start fading out trace after a given trace length?
            fade_out_trace=True,
        )
        advanced_style_params = dict(
            # Amount by which opacity is reduced each frame if trace is being faded out
            trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
            # Trace sum amount before which traces shouldn't start being faded out
            amount_to_not_fade_out_trace_before=1.5, #500, #1.25, #7.5,
            # Buff to prevent superposition between traces (darkens colors and looks ugly)
            line_trace_overlap_buff=DEFAULT_TRACE_OVERLAP_BUFF,
            # Traces to calculate at each frame (to reduce blockiness)
            precision_multiplier_if_trace_too_rough=3,
            # Max number of trace lines to have not faded out at a given frame
            max_number_of_trace_lines=100
        )

        systems = DynamicalSystemFamily(
            **base_params,
            **style_params,
            **advanced_style_params
        )
        systems.add_to_scene()

        self.wait(60)