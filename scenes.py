from manimlib import *
from dynamical_systems import *
import numpy as np
import math


class HalvorsenAttractorScene(ExpandedThreeDScene):
    scale_factor = 0.28
    speed_rate = 0.35
    width = 2
    point_radius = 0.015
    stroke_opacity = 1
    point_color = GREY_B
    color = 'magenta'
    max_velocity = 18
    trace_fadeout_decrease_factor = 0.085
    amount_to_not_fade_out_trace_before = 6.5
    precision_multiplier_if_trace_too_rough = 3
    max_number_of_trace_lines = 100

    def construct(self) -> None:
        a = 1.89
        self.dx = lambda x,y,z: - a * x - 4 * y - 4 * z - (y)**2
        self.dy = lambda x,y,z: - a * y - 4 * z - 4 * x - (z)**2
        self.dz = lambda x,y,z: - a * z - 4 * x - 4 * y - (x)**2
        self.set_up_camera(rate=0.003, rotation_center=np.array([-0.60324335, -0.82967388, -0.90370904]))
        self.set_initial_positions(
            range_params=[[-1.25, 1.15, 0.4]]*3,
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
        )
        systems = self._get_dynamical_systems()
        systems.add_to_scene()
        self.wait(5)


class MultipleLorentzAttractorScene(ExpandedThreeDScene):
    scale_factor = 0.125
    speed_rate = 0.325
    width = 2.5
    point_radius = 0.015
    stroke_opacity = 1
    point_color = GREY_B
    color = 'teal1'
    max_velocity = 20
    trace_fadeout_decrease_factor = 0.1
    amount_to_not_fade_out_trace_before = 7.5
    precision_multiplier_if_trace_too_rough = 3

    def construct(self) -> None:
        sigma = 10
        beta = 8/3  
        rho = 28    
        self.dx = lambda x,y,z: sigma * (y - x)
        self.dy = lambda x,y,z: rho * x - y - x * z
        self.dz = lambda x,y,z: x * y - beta * z
        self.set_up_camera(rate=0.00975,rotation_center=np.array([0, 0, 3.5]))
        self.set_initial_positions(
            range_params=[[0, 2, 0.5], [-1, 1, 0.5], [0, 2, 0.5]],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
        )
        systems = self._get_dynamical_systems()
        systems.add_to_scene()
        self.wait(10)


class ChenLeeAttractorScene(ExpandedThreeDScene):
    scale_factor = 0.15
    speed_rate = .4
    width = 1.8
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'purple2'
    max_velocity = 15
    trace_fadeout_decrease_factor = 0.025  # 0.05, #0.3
    amount_to_not_fade_out_trace_before = 3   #2, #0.25, #500, #1.25, #7.5,
    precision_multiplier_if_trace_too_rough = 3
    max_number_of_trace_lines = 15
    # Unused style for long trace
    # trace_fadeout_decrease_factor=0.1,
    # amount_to_not_fade_out_trace_before=7.5,
    # precision_multiplier_if_trace_too_rough=3,
    # max_number_of_trace_lines=10,

    def construct(self):
        alpha = 5
        beta = -10  
        delta = -0.38    
        self.dx = lambda x,y,z: alpha * x - y * z
        self.dy = lambda x,y,z: beta * y + x * z
        self.dz = lambda x,y,z: delta * z + x * y / 3
        r1 = Rotation.from_rotvec((np.pi/2 - np.pi/8) * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.set_up_camera(rate=0.006, rotation=rot)
        initial_positions = set([
            (x, y, sgn * z) for x in np.arange(0, 1, 0.5)
            for y in np.arange(-1, 1, 0.5)
            for z in np.arange(.75, 5.1, .5)
            for sgn in [-1, 1]
        ])
        self.initial_positions = self.remove_z_axis(initial_positions)
        systems = self._get_dynamical_systems()
        systems.add_to_scene()
        self.wait(15)


class AizawaAttractorScene(ExpandedThreeDScene):
    scale_factor = 1/0.55
    speed_rate = 1
    width = 2.5
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'dark_purple'
    max_velocity = 7 # 8.5
    trace_fadeout_decrease_factor = 0.05
    amount_to_not_fade_out_trace_before = 1.5 #1
    precision_multiplier_if_trace_too_rough = 1
    max_number_of_trace_lines = 100
    # Unused style for long trace
    # trace_fadeout_decrease_factor=0.1 #0.05, #.025, # 0.3
    # amount_to_not_fade_out_trace_before=7.5
    # line_trace_overlap_buff=0.0225
    # precision_multiplier_if_trace_too_rough=3

    def construct(self):
        a = 0.95
        b = 0.7
        c = 0.6
        d = 3.5
        e = 0.25
        f = 0.1
        self.dx = lambda x,y,z: (z - b) * x - d * y
        self.dy = lambda x,y,z: d * x + (z - b) * y
        self.dz = lambda x,y,z: c + a * z - z**3 / 3 - (x**2 + y**2) * (1 + e * z) + f * z * x**3
        self.set_up_camera(rate=0.006, rotation_center=np.array([0.00643597, -0.02607911,  1.5]))
        self.set_initial_positions(
            # range_params=[[-1, 1, 0.25], [-0.5, 0.5, 0.5], [-2, 1.1, .5]],
            range_params=[[-1, 1, 0.25], [-0.5, 0.5, 0.25], [0, 2.1, .5]],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
        )
        self.initial_positions = [self.scale_factor * np.array(pos) for pos in self.initial_positions]
        systems = self._get_dynamical_systems()
        systems.add_to_scene()
        self.wait(10)


class ThomasAttractor(ExpandedThreeDScene):
    scale_factor = 1
    speed_rate = 3  # 1.5 
    width = 2.3
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'yellow_red_pastel'
    max_velocity = 0.925
    trace_fadeout_decrease_factor = 0.03
    amount_to_not_fade_out_trace_before = 1.5
    precision_multiplier_if_trace_too_rough = 1
    max_number_of_trace_lines = 30  # 50

    def construct(self):
        beta = 0.19
        scale = 1.5
        self.dx = lambda x,y,z: -beta * x + math.sin(y*scale) / scale
        self.dy = lambda x,y,z: -beta * y + math.sin(z*scale) / scale
        self.dz = lambda x,y,z: -beta * z + math.sin(x*scale) / scale
        self.set_up_camera(rate=0.006)  # 0.00975
        self.set_initial_positions(
            range_params=[[-1.5, 1.61, 0.6]] * 3,
            range_type=RangeType.ASSYMETRIC,
        )
        self.initial_positions = [1.4 * np.array(pos) for pos in self.initial_positions]
        systems = self._get_dynamical_systems()
        systems.add_to_scene()
        self.wait(10)


class SakaryaAttractor(ExpandedThreeDScene):
    scale_factor = 0.225
    speed_rate = 1  #.2
    width = 2.3
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'blue2'
    max_velocity = 10
    trace_fadeout_decrease_factor = 0.1
    amount_to_not_fade_out_trace_before = 1.5
    precision_multiplier_if_trace_too_rough = 3
    max_number_of_trace_lines = 100

    def construct(self):
        a = 0.4
        b = 0.3
        self.dx = lambda x,y,z: -x + y + (y * z)
        self.dy = lambda x,y,z: -x - y + (a * x * z)
        self.dz = lambda x,y,z: z - (b * x * y)
        self.set_up_camera(rate=0.006)
        self.set_initial_positions(
            range_params=[[-1.5, 1.51,  0.6]] * 3,
            range_type=RangeType.ASSYMETRIC,
        )
        systems = self._get_dynamical_systems()
        systems.add_to_scene()
        self.wait(5)


class ChenCelikovskyAttractor(ExpandedThreeDScene):
    # snapshot_time_domain = [0, 50]
    scale_factor = 0.125
    speed_rate = 0.25
    width = 2.3
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    # color = 'blue2'
    color = 'green4_similar_to_teal1'
    max_velocity = 35
    trace_fadeout_decrease_factor = 0.1
    amount_to_not_fade_out_trace_before = 7
    precision_multiplier_if_trace_too_rough = 3
    # max_number_of_trace_lines = 100

    def construct(self):
        alpha = 36
        beta = 3
        delta = 20
        self.dx = lambda x,y,z: alpha * (y - x)
        self.dy = lambda x,y,z: - x * z + delta * y
        self.dz = lambda x,y,z: x * y - beta * z
        system_avg_center = np.array([0.01420126, 0.01389016, 2.37932611])
        self.set_up_camera(rate=0.006, rotation_center=system_avg_center)
        self.set_initial_positions(
            range_params=[[system_avg_center[i]-1, system_avg_center[i]+1, 0.5] for i in range(3)],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True
        )
        # Add this?
        # self.initial_positions = [system_avg_center + 2 * np.array(pos) for pos in self.initial_positions]
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            color_coded=True,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(30)


class ThreeScrollAttractor(ExpandedThreeDScene):
    snapshot_time_domain = [0, 50]
    scale_factor = .02
    speed_rate = 0.15
    width = 2
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'teal1'
    # color = 'green4_similar_to_teal1'
    max_velocity = 400
    trace_fadeout_decrease_factor = 0.05
    amount_to_not_fade_out_trace_before = 60
    precision_multiplier_if_trace_too_rough = 10 # 15
    # max_number_of_trace_lines = 100

    def construct(self):
        alpha = 40
        c = 55
        beta = 1.833
        delta = 0.16
        epsilon = 0.65
        zeta = 20
        self.dx = lambda x,y,z: alpha * (y - x) + delta * x * z
        self.dy = lambda x,y,z: c * x - x * z + zeta * y
        self.dz = lambda x,y,z: beta * z + x * y - epsilon * x**2
        system_avg_center = np.array([0.02280541, 0.01407737, 2.21027117])
        self.set_up_camera(rate=0.006, rotation_center=system_avg_center)
        self.set_initial_positions(
            range_params=[[-2, 0, 1], [0, 2, 1], [0, 1, .5]],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True
        )
        print(len(self.initial_positions))
        # self.initial_positions = [[2, 2, .5], [3, 3, 0], [.5, .5, .5], [-1, -2, .5], [-1, 2, 1]]
        # self.initial_positions = [system_avg_center + 3 * np.array(pos) for pos in self.initial_positions]
        systems = self._get_dynamical_systems(
            # is_snapshot=True,
            # is_for_n_positions=1,
            # color_coded=False,
            # fade_out_trace=False,
        )
        systems.add_to_scene()
        self.wait(3)
        # self.wait(60)
