import numpy as np
import math
import copy

from manimlib import *
from dynamical_systems.constants import *
from dynamical_systems.abstract_dynamical_system import *
from typing import List
from colour import Color


class DynamicalSystemSnapshot(AbstractDynamicalSystem):
    """A frozen-in-time dynamical system."""

    # TODO: Not sure I like this idea a lot, but maybe implement UnilateralDynamicalSystem and then make DynamicalSystem
    # support being billateral

    def __init__(
        self,
        scene,
        init_pos,
        time_domain, 
        dx, 
        dy, 
        dz=None, 
        show_point=True, 
        color_code_velocity=False, 
        fade_out_trace=False,
        style=BASE_STYLE,
        **kwargs
    ):
        assert time_domain[0] <= 0 and time_domain[1] >= 0, "Time domain of the system must contain t=0"
        self.time_domain = time_domain
        self.color_code_velocity = color_code_velocity
        super().__init__(scene, init_pos, dx, dy, dz, show_point, color_code_velocity, fade_out_trace, style, **kwargs)


    def build_solution(self):
        self.forward_trace = self._build_solution_piece(is_forward=True)
        self.extreme_point_forward = self.get_np_array_from_list(copy.deepcopy(self.coords))

        self.backward_trace = self._build_solution_piece(is_forward=False)
        self.extreme_point_backward = self.get_np_array_from_list(copy.deepcopy(self.coords))

        self.trace = VGroup(self.trace, self.backward_trace, self.forward_trace)
        self.point = SurfaceMesh(Sphere(), resolution=(5, 5), color=self.point_color).scale(self.point_radius).move_to(self.extreme_point_forward)


    def _build_solution_piece(self, is_forward, time_delta=DEFAULT_TIME_DELTA):
        """Constructs the trace, either time-forward or time-backwards.
        is_forward = True for forward trace, False for backward."""

        # TODO: Remove trace definition inside this function and directly add corners to self.point_and_trace.trace.
        # Comment on the todo: wasn't able to figure this out yet since adding all trace points 
        # to a list before adding them to the trace compromises precision of the approximation
        trace = self.get_base_trace()
        dt = time_delta
        self.coords = self.get_list_from_np_array(self.init_pos_vector)
        self.last_coords = self.copy_coords(self.last_coords, self.coords)

        n_of_iterations = math.floor(abs(self.time_domain[is_forward]) / dt)
        should_log_build_progress = self.color_code_velocity and n_of_iterations > 1000

        if should_log_build_progress:
            print(f"Building solution piece. Total of iterations to build: {n_of_iterations}")

        sum_of_coords = ORIGIN

        import time
        time_sum = 0

        ITERATION_MODULUS = 1000

        for i in range(n_of_iterations):

            if i % 1000 == 0 and i != 0:
                print(f"Average point: {sum_of_coords / i}") # Average point
            
            if should_log_build_progress and i % ITERATION_MODULUS == 0 and i != 0:
                print(f"{i} iterations completed")
                
            sum_of_coords += self.last_coords

            maybe_updated_coords = self.update_coords(copy.deepcopy(self.coords), dt)
            self.is_updated_coord_too_far = np.linalg.norm(
                self.get_np_array_from_list(maybe_updated_coords) - self.get_np_array_from_list(self.last_coords),
                2
            ) > self.trace_precision_increase_threshold

            if self.is_updated_coord_too_far:
                for i in range(self.precision_multiplier_if_trace_too_rough - 1):
                    mult = self.precision_multiplier_if_trace_too_rough
                    self.last_coords = self.copy_coords(self.last_coords, self.coords)
                    self.coords = self.update_coords(self.coords, dt/mult)

                    self.second_to_last_coords[i] = self.copy_coords(self.second_to_last_coords[i], self.last_coords)
                    # point = point.move_to(self.get_np_array_from_list(self.adapt_dimensions(self.last_coords)))

            self.last_coords = self.copy_coords(self.last_coords, self.coords)
            self.coords = self.update_coords(self.coords, dt/self.precision_multiplier_if_trace_too_rough if self.is_updated_coord_too_far else dt)


            # self.last_coords = self.copy_coords(self.last_coords, self.coords)
            # self.coords = self.update_coords(self.coords, dt if is_forward else -dt)

            # current_time = time.process_time()
            # if should_log_build_progress and i % ITERATION_MODULUS == 0 and i != 0:
            #     print(f"Adding line to trace")


            # self.update_trace(trace, self.coords, self.last_coords)            

            if len(self.second_to_last_coords) > 0 and self.is_updated_coord_too_far:
                mult = self.precision_multiplier_if_trace_too_rough
                if mult > 1:
                    for i in range(mult - 2):
                        self.update_trace(trace, self.second_to_last_coords[i], self.second_to_last_coords[i+1])
                self.update_trace(trace, self.last_coords, self.second_to_last_coords[mult-2])

            self.update_trace(trace, self.coords, self.last_coords)

            # time_sum += time.process_time() - current_time
            # if should_log_build_progress and i % ITERATION_MODULUS == 0 and i != 0:
            #     print(f"Added line! - this batch took {time_sum} seconds\n")

            if should_log_build_progress and i % ITERATION_MODULUS == 0 and i != 0:
                time_sum = 0

        if should_log_build_progress:
            print("Done building piece!")

        return trace


    def build_solution_with_time_delta(self, time_delta):
        # TODO: This method is inherently inefficient. Refactor it
        self.forward_trace = self._build_solution_piece(is_forward=True, time_delta=time_delta)
        self.extreme_point_forward = self.get_np_array_from_list(copy.deepcopy(self.coords))

        self.backward_trace = self._build_solution_piece(is_forward=False, time_delta=time_delta)
        self.extreme_point_backward = self.get_np_array_from_list(copy.deepcopy(self.coords))

        self.trace = VGroup(self.trace, self.backward_trace, self.forward_trace)
        self.point.move_to(self.extreme_point_forward)


    def add_local_section(self, is_flow_box=False):
        """Adds a local section or flow box on the initial position."""

        assert self.dimension == 2, "Can't currently calculate local sections or flow boxes for 3D systems"

        self.local_section = self._calculate_local_section_or_flow_box(
                self.get_list_from_np_array(self.init_pos_vector),
                is_flow_box
            )

        self.scene.add(self.local_section).bring_to_back(self.local_section)

    
    def get_solution_through_point(self, point):
        return DynamicalSystemSnapshot(
            scene=self.scene,
            init_pos=self.get_list_from_np_array(point),
            time_domain=self.flow_box_solution_time_domain,
            dx=self.functions[Coords.X],
            dy=self.functions[Coords.Y],
            dz=self.functions[Coords.Z] if self.dimension == 3 else None,
            show_point=False,
            color=self.flow_box_trace_color,
            width=self.flow_box_trace_width
        )

    def add_to_scene(self):
        self.scene.add(self.trace, self.point)
        for m in self.trace.submobjects:
            self.scene.add(m)

        if not self.show_point:
            self.point.set_opacity(0)



class DynamicalSystem(AbstractDynamicalSystem):
    """A dynamical system that updates its position on each frame."""

    def __init__(
        self,
        scene: Scene | ThreeDScene,
        init_pos: List[float],
        dx,
        dy,
        dz=None,
        show_point: bool=True,
        color_code_velocity=False,
        fade_out_trace=False,
        style: DynamicalSystemStyle=BASE_STYLE,
        **kwargs
        ):

        self.d_list = [[pos_coord] for pos_coord in init_pos] # list of (x,y) coords of the system
        self.get_point_func = self.get_point
        self.get_trace_func = self.get_trace

        super().__init__(scene, init_pos, dx, dy, dz, show_point, color_code_velocity, fade_out_trace, style, **kwargs)


    def get_point(self, point, dt):
        """Updates coordinates of the system's point."""

        maybe_updated_coords = self.update_coords(copy.deepcopy(self.coords), dt)
        self.is_updated_coord_too_far = np.linalg.norm(
            self.get_np_array_from_list(maybe_updated_coords) - self.get_np_array_from_list(self.last_coords),
            2
        ) > self.trace_precision_increase_threshold

        if self.is_updated_coord_too_far:
            for i in range(self.precision_multiplier_if_trace_too_rough - 1):
                mult = self.precision_multiplier_if_trace_too_rough
                self.last_coords = self.copy_coords(self.last_coords, self.coords)
                self.coords = self.update_coords(self.coords, dt/mult)
                for axis in self.dimension_axes:
                    self.d_list[axis].append(self.coords[axis])
                self.second_to_last_coords[i] = self.copy_coords(self.second_to_last_coords[i], self.last_coords)
                point = point.move_to(self.get_np_array_from_list(self.adapt_dimensions(self.last_coords)))

        self.last_coords = self.copy_coords(self.last_coords, self.coords)
        self.coords = self.update_coords(self.coords, dt/self.precision_multiplier_if_trace_too_rough if self.is_updated_coord_too_far else dt)
        for axis in self.dimension_axes:
            self.d_list[axis].append(self.coords[axis])

        # if len(self.d_list[0]) % 100 == 0:
        #     print(len(self.d_list[0]), "iterations", "Average point:", np.array([sum(self.d_list[i]) for i in [0,1,2]]) / len(self.d_list[0]))
        
        # print("Point updated - moved to", [round(c, 7) for c in self.coords])

        return point.move_to(self.get_np_array_from_list(self.adapt_dimensions(self.coords)))

    def get_trace(self, trace):
        """Updates coordinates of the system's trace."""
            
        if len(self.second_to_last_coords) > 0 and self.is_updated_coord_too_far:
            mult = self.precision_multiplier_if_trace_too_rough
            if mult > 1:
                for i in range(mult - 2):
                    self.update_trace(trace, self.second_to_last_coords[i], self.second_to_last_coords[i+1])
            self.update_trace(trace, self.last_coords, self.second_to_last_coords[mult-2])


        self.update_trace(trace, self.coords, self.last_coords)
        self.scene.bring_to_front(self.trace)

        # print("Trace updated - moved to", [round(c, 7) for c in self.coords], "from", [round(c, 7) for c in self.last_coords], '\n')


    def build_solution(self):
        # self.point_and_trace.add_updater(self.point_and_trace_func)
        self.point.add_updater(self.get_point_func)
        self.trace.add_updater(self.get_trace_func)


    def pause_update(self):
        self.point.remove_updater(self.get_point_func)
        self.trace.remove_updater(self.get_trace_func)


    def resume_update(self):
        self.point.add_updater(self.get_point_func)
        self.trace.add_updater(self.get_trace_func)


    def add_local_section(self, is_flow_box=False):
        """Adds a local section or flow box on the initial position and moves it along the solution, time-forward."""

        assert self.dimension == 2, "Can't currently calculate local sections for 3D systems"

        def update_local_section(is_flow_box):
            return self._calculate_local_section_or_flow_box(
                [self.d_list[i][-self._d_list_length_on_section_added] for i in range(len(self.d_list))],
                is_flow_box
            )

        self._d_list_length_on_section_added = len(self.d_list[0])
        local_section_updater_function = lambda : update_local_section(is_flow_box)
        self.local_section = always_redraw(local_section_updater_function)

        self.scene.add(self.local_section)#.bring_to_front(self.local_section)
    

    def get_solution_through_point(self, point):
        return DynamicalSystemSnapshot(
            scene=self.scene,
            init_pos=self.get_list_from_np_array(point),
            time_domain=self.flow_box_solution_time_domain,
            dx=self.functions[Coords.X],
            dy=self.functions[Coords.Y],
            dz=self.functions[Coords.Z] if self.dimension == 3 else None,
            show_point=False,
            color=self.flow_box_trace_color,
            width=self.flow_box_trace_width
        )


class BilateralDynamicalSystem(DynamicalSystem):
    """Time-forward and time-backwards dynamical system."""

    def __init__(
        self, 
        scene, 
        init_pos, 
        dx, 
        dy, 
        dz=None, 
        show_point=True, 
        color_code_velocity=False, 
        style=BASE_STYLE, 
        **kwargs
    ):
        super().__init__(scene, init_pos, dx, dy, dz, show_point, color_code_velocity, fade_out_trace=False, style=style, **kwargs)
        
        backwards_functions = self.get_backwards_functions()

        self.forward_system = self
        self.backwards_system = DynamicalSystem(
            scene=scene,
            init_pos=init_pos,
            dx=backwards_functions[Coords.X],
            dy=backwards_functions[Coords.Y],
            dz=backwards_functions[Coords.Z],
            show_point=show_point,
            color_code_velocity=color_code_velocity,
            fade_out_trace=False,
            style=style,
            **kwargs
        )


    def get_backwards_functions(self):
        if self.dimension == 2:
            return [
                lambda x,y: -self.functions[Coords.X](x,y),
                lambda x,y: -self.functions[Coords.Y](x,y),
                None
            ]
        else:
            return [
                lambda x,y,z: -self.functions[Coords.X](x,y,z),
                lambda x,y,z: -self.functions[Coords.Y](x,y,z),
                lambda x,y,z: -self.functions[Coords.Z](x,y,z),
            ]


    def add_to_scene(self):
        self.scene.add(
            self.forward_system.trace, self.backwards_system.trace,
            self.forward_system.point, self.backwards_system.point
        )


    def pause_update(self, pause_only_backward=False):
        self.backwards_system.pause_update()
        if not pause_only_backward:
            self.forward_system.pause_update()


    def resume_update(self, resume_only_backward=False):
        self.backwards_system.resume_update()
        if not resume_only_backward:
            self.forward_system.resume_update()


class DynamicalSystemFamily:
    """Draws multiple dynamical systems of the same system of equations,
    with different initial positions."""

    def __init__(
        self,
        scene,
        initial_positions,
        dx,
        dy,
        dz=None,
        time_domain=DS_SNAPSHOT_DEFAULT_TIME_DOMAIN,
        show_snapshots=False, # Whether to show a DynamicalSystemSnapshot (True) or DynamicalSystem (False)
        show_points=True,
        color_code_velocity=False,
        fade_out_trace=False,
        lower_quality=False,
        style=BASE_STYLE,
        color=BASE_STYLE.color, # can either be a single color or a list of colors to fade
        **kwargs
    ):
        self.scene = scene
        self.systems = []
        self.initial_positions = initial_positions

        colors = self.generate_color_gradient(color)

        # Generate systems
        should_log_build_progress = show_snapshots and color_code_velocity and len(self.initial_positions) > 10
        if should_log_build_progress:
            print(f"Total of systems to build: {len(self.initial_positions)}")
        for i, init_pos in enumerate(self.initial_positions):
            if should_log_build_progress and i % 10 == 0 and i != 0:
                print(f"Built {i} systems")
            parameters = dict(
                    scene=scene,
                    init_pos=init_pos,
                    dx=dx,
                    dy=dy,
                    dz=dz,
                    show_point=show_points,
                    color_code_velocity=color_code_velocity,
                    fade_out_trace=fade_out_trace,
                    style=style,
                    color=colors[i],
                    **kwargs
            )
            if show_snapshots:
                parameters['time_domain'] = time_domain
                solution = DynamicalSystemSnapshot(**parameters)
                if lower_quality:
                    solution.build_solution_with_time_delta(LOW_QUALITY_TIME_DELTA)
            else:
                solution = DynamicalSystem(**parameters)
            self.systems.append(solution)

        if should_log_build_progress:
            print("Done!")

    def add_to_scene(self):
        for system in self.systems:
            system.add_to_scene()

    def remove_from_scene(self):
        for system in self.systems:
            system.remove_from_scene()

    def generate_color_gradient(self, colors: List[Color]):
        if isinstance(colors, str) or isinstance(colors, Color):
            colors = [colors]

        if len(colors) == 1:
            return colors * len(self.initial_positions)
        elif len(colors) == len(self.initial_positions):
            return colors

        for i in range(len(colors)):
            colors[i] = Color(colors[i]) if isinstance(colors[i], str) else colors[i]

        n_of_fades = math.ceil(len(self.initial_positions) / (len(colors) - 1))
        gradient = []
        for i in range(len(colors) - 1):
            gradient += colors[i].range_to(colors[i+1], n_of_fades)

        return gradient


class PhasePlane(DynamicalSystemFamily):
    """Draws a 2D phase plane of the given system."""

    # TODO: calculate color coding limit once and pass it to each system
    def __init__(
        self,
        scene,
        plane,
        dx,
        dy,
        time_domain=DS_SNAPSHOT_DEFAULT_TIME_DOMAIN,
        show_snapshots=False, # Whether to show DynamicalSystemSnapshot's (True) or DynamicalSystem's (False)
        show_points=True,
        color_code_velocity=False,
        lower_quality=False,
        style=BASE_STYLE,
        **kwargs
    ):
        self.show_points = show_points
        step = DS_PHASE_PLANE_DEFAULT_STEP
        # Set up initial positions on plane points
        x_range = [math.ceil(plane.x_range[0]), math.floor(plane.x_range[1]) + step]
        y_range = [math.ceil(plane.y_range[0]), math.floor(plane.y_range[1]) + step]
        initial_positions = [[x,y] for y in np.arange(*y_range, step) for x in np.arange(*x_range, step)]

        super().__init__(
            scene=scene,
            initial_positions=initial_positions,
            dx=dx,
            dy=dy,
            time_domain=time_domain,
            show_snapshots=show_snapshots,
            show_points=show_points,
            color_code_velocity="from_plane" if color_code_velocity else False,
            lower_quality=lower_quality,
            style=style,
            **kwargs
        )
    
    
    def add_to_scene(self):
        for system in self.systems:
            self.scene.add(system.trace)

        if self.show_points:
            for system in self.systems:
                self.scene.add(system.point)


class Bifurcation(PhasePlane):
    def __init__(
        self,
        scene,
        plane,
        dx,
        dy,
        parameter: DecimalNumber,
        time_domain=[0, DS_SNAPSHOT_DEFAULT_TIME_DOMAIN[1]],
        color_code_velocity=False,
        lower_quality=False,
        style=BASE_STYLE,
        **kwargs
        ):

        BIFURCATION_MAX_VALUE = 40

        self.scene = scene
        # self.parameter = parameter # Should be a DecimalNumber
        self.dx = lambda x,y: dx(x,y) if dx(x,y) <= BIFURCATION_MAX_VALUE else BIFURCATION_MAX_VALUE
        self.dy = lambda x,y: dy(x,y) if dy(x,y) <= BIFURCATION_MAX_VALUE else BIFURCATION_MAX_VALUE
        self.plane = plane
        self.time_domain = time_domain
        self.color_code_velocity = color_code_velocity
        self.style = style
        self.lower_quality = lower_quality

        parameter.add_updater(lambda n, dt: n.set_value(n.get_value() + 0.1*dt))
        self.phase_plane = always_redraw(lambda : self.get_updated_phase_plane())


    def get_phase_plane(self):
        return PhasePlane(
            scene=self.scene,
            plane=self.plane,
            dx=self.dx,
            dy=self.dy,
            show_snapshots=True,
            show_points=False,
            time_domain=self.time_domain,
            color_code_velocity=self.color_code_velocity,
            lower_quality=self.lower_quality,
            style=self.style
        )

    def get_updated_phase_plane(self):
        system = self.get_phase_plane()
        mobjs = [s.forward_trace for s in system.systems]
        return VGroup(*mobjs)


    def add_to_scene(self):
        self.scene.add(self.phase_plane)
