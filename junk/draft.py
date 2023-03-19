import sys
# Don't know why but ManimGL doesn't add current working directory as part of the PATH.
# Doing this so I can import dynamical_systems.
sys.path.append('/Users/matiaspalumbo/Documents/Manim stuff/dynamical_systems_module_and_video')

from manimlib import *
from dynamical_systems.dynamical_systems.dynamical_systems_new_source_code import *
import numpy as np
import math
from colour import Color

class HalvorsenAttractorScene(ThreeDScene):
    leave_progress_bars = True

    def set_up_camera(self, rate=0.003):
        def get_dt(dt, offset=0):
            return 0.1 + math.cos(dt + offset)
        # Set up rotation
        r1 = Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.camera.frame.set_orientation(rot)
        # Set up position - average center of the system
        about_point = np.array([-0.67922174, -0.67611461, -0.67617357])
        # about_point = np.array([-0.67922174, -0.67611461, 2])
        # about_point = np.array([-1, -1, -2])
        self.camera.frame.move_to(about_point)
        # Continuously rotate camera
        self.camera.frame.add_updater(
            lambda camFrame, dt: camFrame.rotate(
                angle=rate*2.5 / 2,
                axis=get_dt(dt)*OUT + get_dt(dt, PI/2)*UP + get_dt(dt, PI)*RIGHT,
                # axis=get_dt(dt)*OUT,
                about_point=about_point,
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

    def construct(self):
        a = 1.89
        alpha = .5 # escala el sistema
        halvorsen_x = lambda x,y,z: - a * x - 4 * y - 4 * z - (y/alpha)**2
        halvorsen_y = lambda x,y,z: - a * y - 4 * z - 4 * x - (z/alpha)**2
        halvorsen_z = lambda x,y,z: - a * z - 4 * x - 4 * y - (x/alpha)**2

        self.set_up_camera(rate=0.003)

        bd = 1.25
        step = 0.5 # .25
        initial_positions = set([
            (x, y, z) for x in np.arange(-bd, bd - 0.1, step)
            for y in np.arange(-bd, bd - 0.1, step)
            for z in np.arange(-bd, bd -0.1, step)
        ]) - {(0,0,0)}
        # initial_positions = list(initial_positions)[:1]

        color_index = 4
        style_for_short_trace = dict(
            trace_fadeout_decrease_factor=0.085, #0.05, #.025, # 0.3
            amount_to_not_fade_out_trace_before=0.5, #500, #1.25, #7.5,
            line_trace_overlap_buff=0.0225,
            precision_multiplier_if_trace_too_rough=3,
        )

        params = dict(
            scene=self,
            dx=halvorsen_x,
            dy=halvorsen_y,
            dz=halvorsen_z,
            point_radius=0.015, # parámetro de estilo; es el radio del punto del sistema
            point_color=GREY_B,
            width=2.5,
            speed_rate=0.25,#0.5
        )

        systems = DynamicalSystemFamily(
            initial_positions=initial_positions,
            color_code_velocity="manual",
            velocity_colors=[
                (SOME_VELOCITY_COLORS[color_index][0], 0),
                (SOME_VELOCITY_COLORS[color_index][1], 2),
                (SOME_VELOCITY_COLORS[color_index][2], 15)
            ], # The first and second number don't do anything for now
            fade_out_trace=True,
            **params,
            **style_for_short_trace,
        )
        systems.add_to_scene()

        self.wait(10)

        # more_initial_positions = [
        #     (0.6, 0.6, 0.6),
        #     (0.1, 0.1, 0.1),
        #     # (-1.2, 1.2, 1),
        #     (0, 0, 1.5)
        # ]
        # more_initial_positions = set([(0, y, 0) for y in np.arange(-bd, bd - 0.1, 0.2)]) - {(0,0,0)}
        # more_systems = []
        # alt_color_index = 0
        # for init_pos in more_initial_positions:
        #     more_systems.append(DynamicalSystem(
        #         init_pos=init_pos,
        #         color=BLUE,
        #         color_code_velocity="manual",
        #         velocity_colors=[
        #             (SOME_VELOCITY_COLORS[alt_color_index][0], 0),
        #             (SOME_VELOCITY_COLORS[alt_color_index][1], 2),
        #             (SOME_VELOCITY_COLORS[alt_color_index][2], 15)
        #         ], # The first and second number don't do anything for now
        #         fade_out_trace=True,
        #         **params,
        #         trace_fadeout_decrease_factor=0.085, #0.05, #.025, # 0.3
        #         amount_to_not_fade_out_trace_before=1, #500, #1.25, #7.5,
        #         line_trace_overlap_buff=0.0225,
        #         precision_multiplier_if_trace_too_rough=3,
        #     ))
        #     more_systems[-1].add_to_scene()
        #     self.wait(0.25)
        

        # Para que este sistema se coloree bien, conviene cambiar la constante COLOR_CODING_SCALE_FACTOR
        # a algo mayor. Para el video que está en el drive, la cambié a 3 [edit: ???]
        # self.wait(60)

        # for system in systems.systems:
        #     system.speed_rate = 0.5
        # self.wait(30)





# class MultipleLorentzAttractorScene(ThreeDScene):
#     def set_up_camera(self, rate=0.003):
#         def get_dt(dt, offset=0):
#             return 0.1 + math.cos(dt + offset)

#         # Set rotation
#         r1 = Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
#         r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
#         rot = r2 * r1
#         self.camera.frame.set_orientation(rot)
#         # Set position
#         about_point = np.array([0, 0, 3.5])
#         self.camera.frame.move_to(about_point)
#         # Continuously rotate camera
#         self.camera.frame.add_updater(
#             lambda camFrame, dt: camFrame.rotate(
#                 angle=rate*3.25,
#                 axis=get_dt(dt)*OUT + get_dt(dt, PI/2)*UP + get_dt(dt, PI)*RIGHT,
#                 about_point=about_point,
#             )
#         )

#     def construct(self):
#         sigma = 10
#         beta = 8/3  
#         rho = 28    
#         alpha = 0.125 # escala el sistema
#         lorentz_x = lambda x,y,z: sigma * (y - x)
#         lorentz_y = lambda x,y,z: rho * x - y - x * z / alpha
#         lorentz_z = lambda x,y,z: x * y / alpha - beta * z

#         # Configuramos que la cámara gire lentamente a medida que se traza el sistema
#         self.set_up_camera(rate=0.003)

#         bd = 2
#         step = .5 # .25
#         initial_positions = set([
#             (x, y, z) for x in np.arange(0, bd, step)
#             for y in np.arange(-bd/2, bd/2, step)
#             for z in np.arange(0, bd, step)
#         ])
#         initial_positions -= set([pos for pos in initial_positions if pos[0] == 0 and pos[1] == 0])
#         # initial_positions = list(initial_positions)[4:5]

#         color_index = 3
#         style_for_long_trace = dict(
#             trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
#             amount_to_not_fade_out_trace_before=7.5,
#             line_trace_overlap_buff=0.0225,
#             precision_multiplier_if_trace_too_rough=3,
#         )
#         style_for_short_trace = dict(
#             trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
#             amount_to_not_fade_out_trace_before=1,#0.25, #500, #1.25, #7.5,
#             line_trace_overlap_buff=0.0225,
#             precision_multiplier_if_trace_too_rough=3,
#         )

#         sistema = DynamicalSystemFamily(
#             scene=self,
#             initial_positions=initial_positions,
#             dx=lorentz_x,
#             dy=lorentz_y,
#             dz=lorentz_z,
#             color_code_velocity="manual",
#             fade_out_trace=True,
#             point_radius=0.015, # parámetro de estilo; es el radio del punto del sistema
#             point_color=GREY_B,
#             width=2.5, #2.3
#             speed_rate=0.325,
#             velocity_colors=[
#                 (SOME_VELOCITY_COLORS[color_index][0], 0),
#                 (SOME_VELOCITY_COLORS[color_index][1], 7.5),
#                 (SOME_VELOCITY_COLORS[color_index][2], 20)
#             ], # The first and second number don't do anything for now
#             **style_for_long_trace
#         )

#         # Para que este sistema se coloree bien, conviene cambiar la constante COLOR_CODING_SCALE_FACTOR
#         # a algo mayor. Para el video que está en el drive, la cambié a 3 [edit: ???]
#         sistema.add_to_scene()
#         self.wait(5)
#         # self.wait(20)
#         # self.wait(60)
#         # self.wait(30)
#         # self.wait(120)
#         # self.wait(300)

#         # 20s hd:
#         #  7:16.27 total without improvement
#         #  3:32.98 total with improvement YAY 
















class ChenLeeAttractorScene(ThreeDScene):
    def set_up_camera(self, rate=0.003):
        def get_dt(dt, offset=0):
            return 0.1 + math.cos(dt + offset)

        # Set rotation
        r1 = Rotation.from_rotvec((np.pi/2 - np.pi/8) * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.camera.frame.set_orientation(rot)
        # Set position
        # Continuously rotate camera
        self.camera.frame.add_updater(
            lambda camFrame, dt: camFrame.rotate(
                angle=rate*2,
                axis=get_dt(dt)*OUT + get_dt(dt, PI/2)*UP + get_dt(dt, PI)*RIGHT,
                # about_point=about_point,
            )
        )

    def construct(self):
        alpha = 5
        beta = -10  
        delta = -0.38    
        scale = 0.15 # escala el sistema
        chen_lee_x = lambda x,y,z: alpha * x - y * z / scale
        chen_lee_y = lambda x,y,z: beta * y + x * z / scale
        chen_lee_z = lambda x,y,z: delta * z + (x * y / 3) / scale

        # self.set_up_axes()
        # Configuramos que la cámara gire lentamente a medida que se traza el sistema
        self.set_up_camera(rate=0.003)

        bdx = 1 #1 #2
        bdy = 1
        step = .5#1/8#.5 # .25
        initial_positions = set([
            (x, y, sgn * z) for x in np.arange(0, bdx, step)
            for y in np.arange(-bdy, bdy, step)
            # for z in np.arange(.75, 2.35, .5)
            # for z in np.arange(.75, 3.1, .5) #z increased -> 3
            for z in np.arange(.75, 5.1, .5)
            for sgn in [-1, 1]
        ])
        initial_positions -= set([pos for pos in initial_positions if pos[0] == 0 and pos[1] == 0])
        # initial_positions = list(initial_positions)[4:5]
        # initial_positions = set([(x, y, 1) for y in np.arange(-bd, bd, step)]) - {(0,0,1)}

        color_index = 5
        style_for_long_trace = dict(
            trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
            amount_to_not_fade_out_trace_before=7.5,
            line_trace_overlap_buff=0.0225,
            precision_multiplier_if_trace_too_rough=3,
            max_number_of_trace_lines=10,
        )
        style_for_short_trace = dict(
            trace_fadeout_decrease_factor=0.025, #0.05, #0.3
            amount_to_not_fade_out_trace_before=3, #2, #0.25, #500, #1.25, #7.5,
            line_trace_overlap_buff=0.0225,
            precision_multiplier_if_trace_too_rough=3,
            max_number_of_trace_lines=10# 100,
        )

        systems = DynamicalSystemFamily(
            scene=self,
            initial_positions=initial_positions,
            dx=chen_lee_x,
            dy=chen_lee_y,
            dz=chen_lee_z,
            color_code_velocity="manual",
            fade_out_trace=True,
            point_radius=0.015, # parámetro de estilo; es el radio del punto del sistema
            point_color=GREY_B,
            width=1.8, #2.3, #2.5
            speed_rate=.5,
            velocity_colors=[
                (SOME_VELOCITY_COLORS[color_index][0], 0),
                (SOME_VELOCITY_COLORS[color_index][1], 7.5),
                (SOME_VELOCITY_COLORS[color_index][2], 10)
            ], # The first and second number don't do anything for now
            **style_for_short_trace
        )

        # Para que este sistema se coloree bien, conviene cambiar la constante COLOR_CODING_SCALE_FACTOR
        # a algo mayor. Para el video que está en el drive, la cambié a 3 [edit: ???]
        systems.add_to_scene()
        # self.wait()
        # self.wait(5)
        # self.wait(10)
        # self.wait(15)
        # self.wait(30)
        self.wait(60)
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


        