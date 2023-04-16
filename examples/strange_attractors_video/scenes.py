from manimlib import *
from dynamical_systems import *
import numpy as np
import math


class DoublePendulumTest(Scene):
    def construct(self) -> None:
        n_of_pendulums = 5
        # colors = list(Color(GREEN).range_to(Color(BLUE), n_of_pendulums))
        colors = list(
            Color('#bdc7b7').range_to(Color('#69a297'), math.floor(n_of_pendulums/2))
        ) + list(Color('#69a297').range_to(Color('#487481'), math.floor(n_of_pendulums/2)))
        pendulums = []
        for i in range(len(colors)):
            pendulums.append(DoublePendulum(
                scene=self,
                initial_angle1=2*i/len(colors)*PI,
                initial_angle2=2*i/len(colors)*PI - 1e-5,
                # initial_angle1=PI/2,
                # initial_angle2=PI/2 - i*1e-5,
                color=colors[i],
                point_radius=0.04,
                center=ORIGIN,
                scale_factor=1.75
            ))
            pendulums[i].add_to_scene()

        pendulums.append(DoublePendulum(
            scene=self,
            initial_angle1=0,
            initial_angle2=0,
            # initial_angle1=PI/2,
            # initial_angle2=PI/2 - i*1e-5,
            color=colors[-1],
            point_radius=0.04,
            center=ORIGIN,
            scale_factor=1.7
        ))
        pendulums[-1].add_to_scene()

        pendulums.append(Pendulum(
            scene=self,
            initial_angle=PI/2,
            color=RED,
            point_radius=0.04,
            center=ORIGIN,
            scale_factor=1.7
        ))
        pendulums[-1].add_to_scene()

        pendulums[0].add_center_point()
        self.wait(5)


class TestScene(ThreeDScene):
    WAIT_TIME = 2.5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        sigma = 10
        beta = 8/3  
        rho = 28
        scale_factor = 0.125
        dx = lambda x,y,z: sigma * (y - x)
        dy = lambda x,y,z: rho * x - y - x * z
        dz = lambda x,y,z: x * y - beta * z
        color = 'teal1'
        self.initial_position = (0.0, -1.0, 1.5)
        self.params = dict(
            scene=self,
            dx=lambda x, y, z: scale_factor * dx(x/scale_factor, y/scale_factor, z/scale_factor),
            dy=lambda x, y, z: scale_factor * dy(x/scale_factor, y/scale_factor, z/scale_factor),
            dz=lambda x, y, z: scale_factor * dz(x/scale_factor, y/scale_factor, z/scale_factor),
            point_radius=0.015,
            point_color=GREY_B,
            width=2.5,
            speed_rate=2,
            velocity_colors=[
                (SOME_VELOCITY_COLORS[color][0], 1),
                (SOME_VELOCITY_COLORS[color][1], 0),
                (SOME_VELOCITY_COLORS[color][2], 20)
            ], 
            trace_fadeout_decrease_factor=0.05,
            amount_to_not_fade_out_trace_before=10,
            precision_multiplier_if_trace_too_rough=3,
        )

    def construct(self):
        self._test_color_coded_fading_dynamical_system()
        self._test_non_color_coded_dynamical_system()
        self._test_color_coded_dynamical_system_snapshot()
        self._test_dynamical_system_snapshot()
        
    def _test_color_coded_fading_dynamical_system(self):
        self.add_label('Color-coded fading system')

        systems = DynamicalSystemFamily(
            initial_positions=[self.initial_position],
            color_code_velocity="manual",
            fade_out_trace=True,
            **self.params
        )
        systems.add_to_scene()
        
        self.wait()
        self.clear()

    def _test_non_color_coded_dynamical_system(self):
        self.add_label('Regular, non-color-coded system')
        
        systems = DynamicalSystemFamily(
            initial_positions=[self.initial_position],
            **self.params
        )
        systems.add_to_scene()
        
        self.wait()
        self.clear()

    def _test_color_coded_dynamical_system_snapshot(self):
        self.add_label('Color-coded dynamical system snapshot')

        systems = DynamicalSystemFamily(
            initial_positions=[self.initial_position],
            color_code_velocity="manual",
            show_snapshots=True,
            **self.params
        )
        systems.add_to_scene()
        
        self.wait()
        self.clear()

    def _test_dynamical_system_snapshot(self):
        self.add_label('Regular dynamical system snapshot')
        
        systems = DynamicalSystemFamily(
            initial_positions=[self.initial_position],
            show_snapshots=True,
            **self.params
        )
        systems.add_to_scene()
        
        self.wait()
        self.clear()

    def add_label(self, label):
        self.add(Text(label).scale(.7).to_corner(UL))

    def wait(self):
        super().wait(self.WAIT_TIME)


class HalvorsenAttractorScene(ExpandedThreeDScene):
    # snapshot_time_domain=[0,200]
    scale_factor = 0.28
    speed_rate = 0.35
    width = 1.8
    point_radius = 0.015
    stroke_opacity = 1
    point_color = GREY_B
    color = 'magenta2'
    max_velocity = 18
    trace_fadeout_decrease_factor = 0.085
    amount_to_not_fade_out_trace_before = 4 # 6.5
    precision_multiplier_if_trace_too_rough = 1  # 3
    max_number_of_trace_lines = 100

    def construct(self) -> None:
        self.camera
        a = 1.89
        self.dx = lambda x,y,z: - a * x - 4 * y - 4 * z - (y)**2
        self.dy = lambda x,y,z: - a * y - 4 * z - 4 * x - (z)**2
        self.dz = lambda x,y,z: - a * z - 4 * x - 4 * y - (x)**2
        # self.set_up_camera(rate=0.003, rotation_center=np.array([-0.60324335, -0.82967388, -0.90370904]))
        self.set_up_camera(rate=0.003)
        self.set_up_camera(
            rate=0,
            rotation=Rotation.from_rotvec(np.array([0.06975916, 0.8150344,  1.23409955])),
            rotation_center=np.array([-0.74296151, -0.7326116,  -0.73024724]),
        )
        # self.set_up_camera(rate=0, rotation=Rotation.from_rotvec(np.array([-0.81552564,  1.31243522,  1.62873928])))
        self.set_initial_positions(
            # range_params=[[-1.25, 1.15, 0.4]]*3,
            range_params=[[-0.1, 0.1, 0.035]]*3,
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
            return_position=0
        )
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()

        # self.wait(10)
        self.wait(90)
        # self.wait(180)


class LorentzAttractorScene(ExpandedThreeDScene):
    scale_factor = 0.125
    speed_rate = 0.325
    width = 2.25  # 2.5
    point_radius = 0.015
    stroke_opacity = 1
    point_color = GREY_B
    color = 'teal1'
    max_velocity = 20
    trace_fadeout_decrease_factor = 0.1
    amount_to_not_fade_out_trace_before = 7.5
    precision_multiplier_if_trace_too_rough = 3
    max_number_of_trace_lines = 250

    def construct(self) -> None:
        sigma = 10
        beta = 8/3  
        rho = 28    
        self.dx = lambda x,y,z: sigma * (y - x)
        self.dy = lambda x,y,z: rho * x - y - x * z
        self.dz = lambda x,y,z: x * y - beta * z
        self.set_up_camera(rate=0.003, rotation_center=np.array([0, 0, 3.5]))
        self.set_initial_positions(
            range_params=[[0, 2.1, 0.5], [-1, 1, 0.5], [0, 2, 0.5]],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
            return_position=0,
        )
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


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
        self.set_up_camera(rate=0.003, rotation=rot, rotate_on_axis=Coords.Z)
        initial_positions = set([
            (x, y, sgn * z) for x in np.arange(0, 1, 0.5)
            for y in np.arange(-1, 1, 0.5)
            for z in np.arange(.75, 5.1, .5)
            for sgn in [-1, 1]
        ])
        self.initial_positions = self.remove_z_axis(initial_positions)
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


class AizawaAttractorScene(ExpandedThreeDScene):
    snapshot_time_domain = [0, 50]
    scale_factor = 2
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
        self.set_up_camera(rate=0.003, rotation_center=np.array([0.00643597, -0.02607911,  1.5]))
        self.set_initial_positions(
            range_params=[[-1, 1, 0.25], [-0.5, 0.5, 0.25], [0, 2.1, .5]],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
        )
        self.initial_positions = [self.scale_factor * np.array(pos) for pos in self.initial_positions]
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


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
        self.set_up_camera(rate=0.003)  # 0.00975
        self.set_initial_positions(
            range_params=[[-1.5, 1.61, 0.6]] * 3,
            range_type=RangeType.ASSYMETRIC,
        )
        self.initial_positions = [1.4 * np.array(pos) for pos in self.initial_positions]
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


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
        self.set_up_camera(rate=0.003)
        self.set_initial_positions(
            range_params=[[1.5,  0.6]] * 3,
            range_type=RangeType.SYMMETRIC,
        )
        systems = self._get_dynamical_systems(
            is_for_n_positions=0,
            fade_out_trace=True
        )
        systems.add_to_scene()
        self.wait(15)


class ChenCelikovskyAttractor(ExpandedThreeDScene):
    snapshot_time_domain = [0, 100]
    scale_factor = 0.125
    speed_rate = 0.25
    width = 2
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    # color = 'blue2'
    color = 'green4_similar_to_teal1'
    max_velocity = 38
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
        self.set_up_camera(rate=0.003, rotation_center=system_avg_center)
        self.set_initial_positions(
            range_params=[[-1, 1, 0.5], [-1, 1, 0.5], [3, 5, 0.5]],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True
        )
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


class ThreeScrollAttractor(ExpandedThreeDScene):
    snapshot_time_domain = [0, 50]
    scale_factor = .02
    speed_rate = 0.15
    width = 2
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'terracota'
    max_velocity = 400
    trace_fadeout_decrease_factor = 0.025
    amount_to_not_fade_out_trace_before = 60
    precision_multiplier_if_trace_too_rough = 10
    max_number_of_trace_lines = 2500

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
        self.set_up_camera(rate=0.003, rotation_center=system_avg_center)
        self.set_initial_positions(
            range_params=[[-2, 0, 1], [0, 2, 1], [0, 1, .5]],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True
        )
        self.initial_positions = [
            np.array([5, 5, 1]),
            np.array([0.1, 0.1, 4]),
            np.array([-5, -5, 1]),
            ]
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


class HadleyAttractor(ExpandedThreeDScene):
    snapshot_time_domain = [0, 50]
    scale_factor = 1.6
    speed_rate = 1
    width = 2
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'sea_blue'
    max_velocity = 18
    trace_fadeout_decrease_factor = 0.05
    amount_to_not_fade_out_trace_before = 5
    precision_multiplier_if_trace_too_rough = 3 # 15
    max_number_of_trace_lines = 100

    def construct(self):
        alpha = 0.2
        beta = 4
        zeta = 8
        delta = 1
        self.dx = lambda x,y,z: - y**2 - z**2 - alpha * x + alpha * zeta
        self.dy = lambda x,y,z: x * y - beta * x * z - y + delta
        self.dz = lambda x,y,z: beta * x * y + x * z - z
        system_avg_center = np.array([[1.26852126, 0.7837236, 0.41510452]])
        self.set_up_camera(rate=0.003, rotation_center=system_avg_center)
        self.set_initial_positions(
            range_params=[[1.01, 0.5], [1, 0.5], [1.01, 0.5]],
            range_type=RangeType.SYMMETRIC,
            remove_z_axis=True
        )
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


class QiChenAttractor(ExpandedThreeDScene):
    snapshot_time_domain = [0, 50]
    scale_factor = 0.05
    speed_rate = 0.15
    width = 2
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'sea_blue'
    max_velocity = 90
    trace_fadeout_decrease_factor = 0.05
    amount_to_not_fade_out_trace_before = 10
    precision_multiplier_if_trace_too_rough = 10 # 15
    max_number_of_trace_lines = 100

    def construct(self):
        alpha = 38
        beta = 8/3
        zeta = 80
        self.dx = lambda x,y,z: alpha * (y - x) + y * z
        self.dy = lambda x,y,z: zeta * x + y - x * z
        self.dz = lambda x,y,z: x * y - beta * z
        system_avg_center = np.array([[0.14887396, 0.07973527, 4.04366204]])
        self.set_up_camera(rate=0.003, rotation_center=system_avg_center)
        self.set_initial_positions(
            range_params=[1, 0.5],
            range_type=RangeType.SIMPLE,
            remove_z_axis=True
        )
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


class RosslerAttractor(ExpandedThreeDScene):
    snapshot_time_domain = [0, 100]
    scale_factor = 0.35
    speed_rate = 2
    width = 2
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'orange_red'
    max_velocity = 7.25
    trace_fadeout_decrease_factor = 0.05
    amount_to_not_fade_out_trace_before = 25
    precision_multiplier_if_trace_too_rough = 8 
    max_number_of_trace_lines = 100

    def construct(self):
        alpha = 0.2
        beta = 0.2
        zeta = 5.7
        self.dx = lambda x,y,z: - y - z
        self.dy = lambda x,y,z: x + alpha * y
        self.dz = lambda x,y,z: beta + z * (x - zeta)
        rotation = Rotation.from_rotvec(
            np.pi/8 * np.array([0, 0, 1])
        ) * Rotation.from_rotvec(np.pi/2 * np.array([1, 0, 0]))
        system_center = np.array([0.07261591, -0.35280944, 2.6])
        self.set_up_camera(
            rate=0.003,
            rotation=rotation,
            rotate_on_axis=Coords.Z,
            rotation_center=system_center
        )
        self.set_initial_positions(
            range_params=[[0, 4, 1]] * 3,
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
        )
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


class FinanceAttractor(ExpandedThreeDScene):
    snapshot_time_domain = [0, 100]
    scale_factor = 1.5
    speed_rate = 3
    width = 2
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'orange_red'
    max_velocity = 4
    trace_fadeout_decrease_factor = 0.05
    amount_to_not_fade_out_trace_before = 25
    precision_multiplier_if_trace_too_rough = 6
    # max_number_of_trace_lines = 100

    def construct(self):
        alpha = 0.001
        beta = 0.2
        zeta = 1.1
        self.dx = lambda x,y,z: (1 / beta - alpha) * x + z + x * y
        self.dy = lambda x,y,z: - beta * y - x **2
        self.dz = lambda x,y,z: - x - zeta * z
        system_center = np.array([-1.11566000e-02, -6.36533981,  2.18073883e-03])
        self.set_up_camera(
            rate=0.004,
            rotation=None,
            rotate_on_axis=Coords.Y,
            rotation_center=system_center
        )
        self.set_initial_positions(
            range_params=[[-1, 1.01, 1]] * 3,
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
        )
        self.initial_positions = [system_center]
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)


class YuWangAttractor(ExpandedThreeDScene):
    snapshot_time_domain = [0, 50]
    scale_factor = 0.225
    speed_rate = 0.25
    width = 2
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'terracota'
    max_velocity = 40
    trace_fadeout_decrease_factor = 0.05
    amount_to_not_fade_out_trace_before = 10
    precision_multiplier_if_trace_too_rough = 50
    max_number_of_trace_lines = 1000

    def construct(self):
        alpha = 10
        beta = 40
        zeta = 2
        delta = 2.5
        self.dx = lambda x,y,z: alpha * (y - x)
        self.dy = lambda x,y,z: beta * x - zeta * x * z
        self.dz = lambda x,y,z: math.exp(x * y) - delta * z
        system_center = np.array([[0.01055654, 0.01495632, 5.60911935]])
        self.set_up_camera(
            rate=0.003,
            rotate_on_axis=Coords.Z,
            rotation_center=system_center
        )
        self.set_initial_positions(
            range_params=[[0.01, 0.5, 0.3], [0.01, 0.5, 0.3], [1, 3, 0.5]],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
        )
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        systems.systems[0].trace_precision_increase_threshold = 0.05
        self.wait(180)


class LorentzMod2Attractor(ExpandedThreeDScene):
    snapshot_time_domain = [0, 50]
    scale_factor = 0.25
    speed_rate = 0.10
    width = 2
    stroke_opacity = 1
    point_radius = 0.015
    point_color = GREY_B
    color = 'terracota'
    max_velocity = 250
    trace_fadeout_decrease_factor = 0.05
    amount_to_not_fade_out_trace_before = 100
    precision_multiplier_if_trace_too_rough = 5
    max_number_of_trace_lines = 1000

    def construct(self):
        alpha = 10
        beta = 40
        zeta = 2
        delta = 2.5
        self.dx = lambda x,y,z: - alpha * x + y**2 - z **2 + alpha * zeta
        self.dy = lambda x,y,z: x * (y - beta * z) + delta
        self.dz = lambda x,y,z: - z + x * (beta * y + z)
        system_center = np.array([[0.30101537, 0.39272164, 0.54582488]])
        self.set_up_camera(
            rate=0.005,
            rotate_on_axis=Coords.Z,
            rotation_center=system_center
        )
        self.set_initial_positions(
            range_params=[[0.01, 0.5, 0.3], [0.01, 0.5, 0.3], [2.5, 3, 0.5]],
            range_type=RangeType.ASSYMETRIC,
            remove_z_axis=True,
        )
        self.initial_positions = list(self.initial_positions) + [[j, 0.5, -i] for i in np.arange(2.5, 3, 0.5) for j in [0.01, 0.2]]
        systems = self._get_dynamical_systems(
            is_snapshot=False,
            is_for_n_positions=0,
            fade_out_trace=True,
        )
        systems.add_to_scene()
        self.wait(180)
