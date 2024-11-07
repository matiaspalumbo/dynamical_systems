from manimlib import *
from dynamical_systems.dynamical_system import *
from dynamical_systems.constants import *
from enum import auto
from strenum import StrEnum
import numpy as np
import math


class RangeType(StrEnum):
    SIMPLE = auto()
    SYMMETRIC = auto()
    ASSYMETRIC = auto()


class ExpandedScene(Scene):
    snapshot_time_domain = [0, 100]
    
    initial_positions = None # To set in construct() method in subclass

    dx = None # To define in construct() method in subclass
    dy = None # To define in construct() method in subclass
    scale_factor = 1

    speed_rate = 1 # Larger speed rate results in less smoothness
    width = 2.5 # Main system trace width
    stroke_opacity = 1 # Main system stroke opacity
    point_radius = 0.05 # 0.015 - radius of the system's point
    point_color = GREY_B # Color of the system's point
    color = 'blue' # Color palette of the system
    max_velocity = 10 # Velocity after which every trace line is the darkest color
    
    # Amount by which opacity is reduced each frame if trace is being faded out
    trace_fadeout_decrease_factor = 0.05 #0.05, #.025, # 0.3
    
    # Trace sum amount before which traces shouldn't start being faded out
    amount_to_not_fade_out_trace_before = 1.5 #500, #1.25, #7.5,
    
    # Buff to prevent superposition between traces (which darkens colors and looks ugly)
    line_trace_overlap_buff = EXP_SCENE_DEFAULT_TRACE_OVERLAP_BUFF
    
    # Traces to calculate at each frame (to reduce blockiness)
    precision_multiplier_if_trace_too_rough = 3
    
    # Max number of trace lines to have not faded out at a given frame
    max_number_of_trace_lines = 500
    
    def set_up_axes(self, axes_length=None):
        axes_config = dict(tip_length=0.2, tip_width=0.2, fill_opacity=0.3)
        params = dict(axis_config=axes_config)
        if axes_length is not None:
            params.update(dict(
                x_range=[-axes_length, axes_length],
                y_range=[-axes_length, axes_length]
            ))
        axes = Axes(**params)
        self.add(axes)
        return axes

    def set_up_number_plane(self):
        stroke_opacity = 0.6
        plane = NumberPlane(
            background_line_style={'stroke_color': GREY_C, 'stroke_opacity': stroke_opacity},
            axis_config={'include_ticks': True, 'stroke_opacity': stroke_opacity},
            faded_line_ratio=0
        )
        self.add(plane)
        return plane

    def set_initial_positions(
            self,
            range_params=[EXP_SCENE_DEFAULT_RANGE_LIMIT, EXP_SCENE_DEFAULT_STEP],
            range_type=RangeType.SIMPLE,
            remove_origin=False, 
            return_position=0
        ):
        """
        Returns a set of pairs according to the given range parameters.
        
        range_params should take a differently formatted list for each type:
        - SIMPLE: needs only one range limit and step passed
            -> [range_lim, step]
        - SYMMETRIC: needs one range limit and step for each coordinate 
            -> [[range_limx, stepx], [range_limy, stepy]]
        - SYMMETRIC: needs both range limits and step for each coordinate 
            -> [[l_rg_limx, u_rg_limx, stepx], [l_rg_limy, u_rg_limy, stepy]]
        """

        if range_type == RangeType.SIMPLE:
            rng = np.arange(-range_params[0], range_params[0], range_params[1])
            initial_positions = set([(x, y) for x in rng for y in rng])
        elif range_type == RangeType.SYMMETRIC:
            rng_x = np.arange(-range_params[0][0], range_params[0][0], range_params[0][1])
            rng_y = np.arange(-range_params[1][0], range_params[1][0], range_params[1][1])
            initial_positions = set([(x, y) for x in rng_x for y in rng_y])
        elif range_type == RangeType.ASSYMETRIC:
            rng_x = np.arange(range_params[0][0], range_params[0][1], range_params[0][2])
            rng_y = np.arange(range_params[1][0], range_params[1][1], range_params[1][2])
            initial_positions = set([(x, y) for x in rng_x for y in rng_y])
        else:
            raise NotImplementedError(f"Don't know how to handle {range_type} range_type")

        self.initial_positions = initial_positions

        if return_position:
            self.initial_positions = list(initial_positions)[return_position:return_position+1]
        elif remove_origin:
            self.initial_positions = initial_positions - {(0,0)}
        
        return initial_positions
        
    def get_velocity_colors(
        self,
        color_index: str='blue',
        max_velocity=EXP_SCENE_DEFAULT_MAX_VELOCITY,
        slow_to_med_weight=1
    ):
        return [
            (SOME_VELOCITY_COLORS[color_index][0], slow_to_med_weight),
            (SOME_VELOCITY_COLORS[color_index][1], 0),
            (SOME_VELOCITY_COLORS[color_index][2], max_velocity)
        ] # The second number doesn't do anything for now

    def _get_scaled_system_functions(self):
        """Returns a scaled system. Larger scale_factor results in larger system."""

        return [
            lambda x, y: self.scale_factor * self.dx(x/self.scale_factor, y/self.scale_factor),
            lambda x, y: self.scale_factor * self.dy(x/self.scale_factor, y/self.scale_factor)
        ]

    def _get_base_system_params(self, is_snapshot, is_for_n_positions):
        assert self.initial_positions is not None, "Should set initial positions before calling this method"
        assert is_for_n_positions <= len(self.initial_positions), "Number of positions requested exceedes total number of positions"
        
        scaled_functions = self._get_scaled_system_functions()
        params = dict(
            scene=self,
            initial_positions=list(self.initial_positions)[:is_for_n_positions] if is_for_n_positions else self.initial_positions,
            dx = scaled_functions[0],
            dy = scaled_functions[1],
            speed_rate = self.speed_rate,
            width = self.width,
            stroke_opacity = self.stroke_opacity,
            point_radius = self.point_radius,
            point_color = self.point_color,
        )
        if is_snapshot:
            params.update(dict(time_domain=self.snapshot_time_domain, show_snapshots=True))
        return params

    def _get_system_params_for_color_coded_velocity(self, fade_out_trace=True):
        return dict(
            color_code_velocity='manual',
            velocity_colors=self.get_velocity_colors(self.color, self.max_velocity),
            max_velocity=self.max_velocity,
            fade_out_trace=fade_out_trace,
            trace_fadeout_decrease_factor=self.trace_fadeout_decrease_factor,
            amount_to_not_fade_out_trace_before=self.amount_to_not_fade_out_trace_before,
            line_trace_overlap_buff=self.line_trace_overlap_buff,
            precision_multiplier_if_trace_too_rough=self.precision_multiplier_if_trace_too_rough,
            max_number_of_trace_lines=self.max_number_of_trace_lines,
        )
    
    def _get_dynamical_systems(
            self,
            is_snapshot=False,
            is_for_n_positions=0, # Can also be a natural number
            color_coded=True,
            fade_out_trace=True,
        ):
        params = dict(
            **(self._get_base_system_params(is_snapshot, is_for_n_positions)),
        )
        if color_coded:
            params.update(self._get_system_params_for_color_coded_velocity(fade_out_trace))

        return DynamicalSystemFamily(**params)


class ExpandedThreeDScene(ThreeDScene):
    snapshot_time_domain = [0, 100]
    
    initial_positions = None # To set in construct() method in subclass

    dx = None # To define in construct() method in subclass
    dy = None # To define in construct() method in subclass
    dz = None # To define in construct() method in subclass
    scale_factor = 1

    speed_rate = 1 # Larger speed rate results in less smoothness
    width = 2.5 # Main system trace width
    stroke_opacity = 1 # Main system stroke opacity
    point_radius = 0.05 # 0.015 - radius of the system's point
    point_color = GREY_B # Color of the system's point
    color = 'blue' # Color palette of the system
    max_velocity = 10 # Velocity after which every trace line is the darkest color
    
    # Amount by which opacity is reduced each frame if trace is being faded out
    trace_fadeout_decrease_factor = 0.1 #0.05, #.025, # 0.3
    
    # Trace sum amount before which traces shouldn't start being faded out
    amount_to_not_fade_out_trace_before = 1.5 #500, #1.25, #7.5,
    
    # Buff to prevent superposition between traces (which darkens colors and looks ugly)
    line_trace_overlap_buff = EXP_SCENE_DEFAULT_TRACE_OVERLAP_BUFF
    
    # Traces to calculate at each frame (to reduce blockiness)
    precision_multiplier_if_trace_too_rough = 3
    
    # Max number of trace lines to have not faded out at a given frame
    max_number_of_trace_lines = 500
        
    def set_up_camera(
        self,
        rate=EXP_SCENE_DEFAULT_CAMERA_ROTATION_RATE,
        rotation=EXP_SCENE_DEFAULT_CAMERA_ROTATION,
        rotation_center=ORIGIN,
        rotate_on_axis=None,
        rotate=True
    ):
        # Set up rotation
        if rotation is not None:
            self.camera.frame.set_orientation(rotation)
        # Set up rotation center - in most cases, average center of the system
        self.camera.frame.move_to(rotation_center)

        def get_dt(dt, offset=0):
            return 0.1 + math.cos(dt + offset)

        if rotate:
            # Continuously rotate camera
            if rotate_on_axis is not None:
                axes = [RIGHT, UP, OUT]
                rotation_func = lambda t: get_dt(t) * axes[rotate_on_axis]
            else:
                rotation_func = lambda t:  get_dt(t, PI/2) * UP

            def _rotate_with_logs(camFrame, dt):
                camFrame.rotate(
                    angle=rate,
                    axis=(rotation_func)(dt),
                    about_point=rotation_center,
                )

            self.camera.frame.add_updater(
                lambda camFrame, dt: _rotate_with_logs(camFrame, dt)
            )
    
    def set_up_axes(self, color_axes=False):
        axes_length = 50
        tip_width = 0.2 
        tip_length = 0.2
        fill_opacity = 0.3
        params = dict(
            x_range=[-axes_length, axes_length],
            y_range=[-axes_length, axes_length],
            z_range=[-axes_length, axes_length]
        )
        if color_axes:
            params.update(dict(
                x_axis_config=dict(tip_length=tip_width, tip_width=tip_length, fill_opacity=fill_opacity, color=RED),
                y_axis_config=dict(tip_length=tip_width, tip_width=tip_length, fill_opacity=fill_opacity, color=BLUE),
                z_axis_config=dict(tip_length=tip_width, tip_width=tip_length, fill_opacity=fill_opacity, color=GREEN),
            ))
        else:
            params.update(dict(
                axis_config=dict(tip_length=tip_width, tip_width=tip_length, fill_opacity=fill_opacity),
                z_axis_config=dict(tip_length=tip_width, tip_width=tip_length, fill_opacity=fill_opacity),
            ))
        axes = ThreeDAxes(**params)
        self.add(axes)
        return axes

    def set_initial_positions(
            self,
            range_params=[EXP_SCENE_DEFAULT_RANGE_LIMIT, EXP_SCENE_DEFAULT_STEP],
            range_type=RangeType.SIMPLE,
            remove_z_axis=False,
            remove_origin=False, 
            return_position=0,
            scale_by=None
        ):
        """
        Returns a set of 3-uples according to the given range parameters.
        
        range_params should take a differently formatted list for each type:
        - SIMPLE: needs only one range limit and step passed
            -> [range_lim, step]
        - SYMMETRIC: needs one range limit and step for each coordinate 
            -> [[range_limx, stepx], [range_limy, stepy], [range_limz, stepz]]
        - SYMMETRIC: needs both range limits and step for each coordinate 
            -> [[l_rg_limx, u_rg_limx, stepx], [l_rg_limy, u_rg_limy, stepy], [l_rg_limz, u_rg_limz, stepz]]
        """

        if range_type == RangeType.SIMPLE:
            rng = np.arange(-range_params[0], range_params[0], range_params[1])
            initial_positions = set([(x, y, z) for x in rng for y in rng for z in rng])
        elif range_type == RangeType.SYMMETRIC:
            rng_x = np.arange(-range_params[0][0], range_params[0][0], range_params[0][1])
            rng_y = np.arange(-range_params[1][0], range_params[1][0], range_params[1][1])
            rng_z = np.arange(-range_params[2][0], range_params[2][0], range_params[2][1])
            initial_positions = set([(x, y, z) for x in rng_x for y in rng_y for z in rng_z])
        elif range_type == RangeType.ASSYMETRIC:
            rng_x = np.arange(range_params[0][0], range_params[0][1], range_params[0][2])
            rng_y = np.arange(range_params[1][0], range_params[1][1], range_params[1][2])
            rng_z = np.arange(range_params[2][0], range_params[2][1], range_params[2][2])
            initial_positions = set([(x, y, z) for x in rng_x for y in rng_y for z in rng_z])
        else:
            raise NotImplementedError(f"Don't know how to handle {range_type} range_type")

        self.initial_positions = initial_positions

        if return_position:
            self.initial_positions = list(initial_positions)[return_position:return_position+1]
        elif remove_z_axis:
            self.initial_positions = self.remove_z_axis(initial_positions)
        elif remove_origin:
            self.initial_positions = initial_positions - {(0,0,0)}

        if scale_by is not None:
            self.initial_positions = [list(scale_by * np.array(pos)) for pos in self.initial_positions]
        
        return initial_positions
    
    def remove_z_axis(self, positions):
        positions -= set([pos for pos in positions if pos[0] == 0 and pos[1] == 0])
        return positions
        
    def get_velocity_colors(
        self,
        color_index: str='blue',
        max_velocity=EXP_SCENE_DEFAULT_MAX_VELOCITY,
        slow_to_med_weight=1
    ):
        return [
            (SOME_VELOCITY_COLORS[color_index][0], slow_to_med_weight),
            (SOME_VELOCITY_COLORS[color_index][1], 0),
            (SOME_VELOCITY_COLORS[color_index][2], max_velocity)
        ] # The second number doesn't do anything for now

    def _get_scaled_system_functions(self):
        """Returns a scaled system. Larger scale_factor results in larger system."""

        return [
            lambda x, y, z: self.scale_factor * self.dx(x/self.scale_factor, y/self.scale_factor, z/self.scale_factor),
            lambda x, y, z: self.scale_factor * self.dy(x/self.scale_factor, y/self.scale_factor, z/self.scale_factor),
            lambda x, y, z: self.scale_factor * self.dz(x/self.scale_factor, y/self.scale_factor, z/self.scale_factor)
        ]

    def _get_base_system_params(self, is_snapshot, is_for_n_positions):
        assert self.initial_positions is not None, "Should set initial positions before calling this method"
        assert is_for_n_positions <= len(self.initial_positions), "Number of positions requested exceedes total number of positions"
        
        scaled_functions = self._get_scaled_system_functions()
        params = dict(
            scene=self,
            initial_positions=list(self.initial_positions)[:is_for_n_positions] if is_for_n_positions else self.initial_positions,
            dx = scaled_functions[0],
            dy = scaled_functions[1],
            dz = scaled_functions[2],
            speed_rate = self.speed_rate,
            width = self.width,
            stroke_opacity = self.stroke_opacity,
            point_radius = self.point_radius,
            point_color = self.point_color,
        )
        if is_snapshot:
            params.update(dict(time_domain=self.snapshot_time_domain, show_snapshots=True))
        return params

    def _get_system_params_for_color_coded_velocity(self, fade_out_trace=True):
        return dict(
            color_code_velocity='manual',
            velocity_colors=self.get_velocity_colors(self.color, self.max_velocity),
            max_velocity=self.max_velocity,
            fade_out_trace=fade_out_trace,
            trace_fadeout_decrease_factor=self.trace_fadeout_decrease_factor,
            amount_to_not_fade_out_trace_before=self.amount_to_not_fade_out_trace_before,
            line_trace_overlap_buff=self.line_trace_overlap_buff,
            precision_multiplier_if_trace_too_rough=self.precision_multiplier_if_trace_too_rough,
            max_number_of_trace_lines=self.max_number_of_trace_lines,
        )
    
    def _get_dynamical_systems(
            self,
            is_snapshot=False,
            is_for_n_positions=0, # Can also be a natural number
            color_coded=True,
            fade_out_trace=True,
            color=TEAL,
        ):
        if fade_out_trace and is_snapshot:
            raise Exception("Can't ask for a faded-out snapshot (yet?)")

        params = dict(
            **(self._get_base_system_params(is_snapshot, is_for_n_positions)),
        )
        if color_coded:
            params.update(self._get_system_params_for_color_coded_velocity(fade_out_trace))

        return DynamicalSystemFamily(**params, color=color)

