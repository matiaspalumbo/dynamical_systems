import numpy as np
import copy

from manimlib import *
from dynamical_systems.constants import *
from dynamical_systems.styles import *

from enum import IntEnum
from colour import Color



class Coords(IntEnum):
    X = 0
    Y = 1
    Z = 2


# TODO: Make style parameters to be only accessed through the 'style' attribute of the system, not as regular attributes

# TODO: implement using coords_to_point when showing phase planes
# TODO: stop using python lists and np.arrays at the same time
# TODO: Remove DynamicalSystemStyle class in favor of dicts
# TODO: update color coding comments to include manual color coding
# TODO: See if high mesh point resolution affects render time severely


class Trace(VGroup):
    def __init__(self, initial_position, *vmobjects: VMobject, **kwargs):
        self.initial_position = initial_position
        super().__init__(*vmobjects, **kwargs)

    def init_points(self):
        self.set_points_as_corners([self.initial_position] * 2)

    @classmethod
    def for_dynamical_system(cls, initial_position, color, width, opacity):
        return cls(
            initial_position=initial_position,
            stroke_color=color,
            stroke_width=width,
            stroke_opacity=opacity,
        ).move_to(initial_position)



class BaseDynamicalSystem(VGroup):
    """Base class for dynamical systems."""

    def __init__(
        self, 
        scene, 
        init_pos, 
        dx, 
        dy, 
        dz=None, 
        show_point=True, 
        color_code_velocity=False, 
        fade_out_trace=False, 
        style: DynamicalSystemStyle = BASE_STYLE, 
        **kwargs
    ):
        self.__dict__.update(style.as_dict()) # Bundle style parameters into a 'style' attribute
        self.__dict__.update(kwargs)
        self.show_point = show_point
        self.scene = scene
        self.dimension_axes = [Coords.X, Coords.Y]
        self.functions = [dx, dy]

        if dz is not None:
            self.dimension_axes.append(Coords.Z)
            self.functions.append(dz)
        
        self.dimension = len(self.dimension_axes)

        assert len(init_pos) == self.dimension, f"Initial position should have {self.dimension} coordinates"
        assert isinstance(scene, Scene), "A Scene object should be passed as the 'scene' parameter"

        self.init_pos_vector = self.get_np_array_from_list(self.adapt_dimensions(init_pos))

        self.coords = copy.deepcopy(list(init_pos)) # Will store the current position of the system
        self.last_coords = copy.deepcopy(list(init_pos)) # Will store the last position of the system

        self.is_updated_coord_too_far = False
        self.second_to_last_coords = [copy.deepcopy(list(init_pos)) for _ in range(self.precision_multiplier_if_trace_too_rough - 1)]

        self.color_code_velocity = color_code_velocity
        self.fade_out_trace = fade_out_trace
        if fade_out_trace:
            self.sum_of_trace_line_lengths = 0
            self.first_index_not_to_fade_out = None
            self.sum_of_all_trace_lines = 0
            self.sum_of_trace_lines_not_faded_out = 0

        # Parameters to handle in system color manager:
            # color_code_velocity

        self._trace_color_manager = SystemColorManager()
        self._trace_color_manager.setup_color_mappings(self)

        if self.dimension == 2:
            point = Dot(radius=self.point_radius).move_to(self.init_pos_vector)
        else:
            point = SurfaceMesh(Sphere(), resolution=(10, 10), color=self.point_color).scale(self.point_radius).move_to(self.init_pos_vector)

        trace = self.get_base_trace()
        self.point = point
        self.trace = trace
        self.trace_update_function = self.get_trace_update_function()

        self.build_solution()

        super().__init__(self.trace, self.point)

    def add_to_scene(self):
        self.scene.add(self.point, self.trace)
        self.scene.bring_to_front(self.trace)

        if not self.show_point:
            self.point.set_opacity(0)

    def remove_from_scene(self):
        self.scene.remove(self.point, self.trace)

    def get_base_trace(self):
        return Trace.for_dynamical_system(
            self.init_pos_vector,
            self.color,
            self.width,
            self.stroke_opacity
        )

    def get_trace_update_function(self): # add_line_objects_to_trace
        if self.fade_out_trace:
            return lambda t, c, lc: self.add_line_objects_to_trace_and_fade_out(t, c, lc)
        elif self.color_code_velocity:
            return lambda t, c, lc: self.add_line_objects_to_trace(t, c, lc)
        else:
            return lambda t, c, lc: self.add_corners_to_trace(t, c)

    def get_new_line_position(self, coords, last_coords):
        last_coords_vector = self.get_np_array_from_list(last_coords)
        coords_vector = self.get_np_array_from_list(coords)
        buff_to_avoid_overlap = self.line_trace_overlap_buff * (coords_vector - last_coords_vector)
        return last_coords_vector + buff_to_avoid_overlap, coords_vector - buff_to_avoid_overlap

    def add_line_objects_to_trace(self, trace, coords, last_coords):
        # Assuming trace is a VGroup object
        new_position = self.get_new_line_position(coords, last_coords)
        new_line = Line(
            new_position[0],
            new_position[1],
            color=self.get_trace_color(),
            stroke_width=self.width,
            stroke_opacity=self.stroke_opacity
        )
        trace.submobjects.append(new_line)
        trace.family.insert(0, new_line)
        trace.refresh_bounding_box()

    def add_line_objects_to_trace_and_fade_out(self, trace: VGroup, coords, last_coords):
        new_position = self.get_new_line_position(coords, last_coords)
        new_line = Line(
            new_position[0],
            new_position[1],
            color=self.get_trace_color(),
            stroke_width=self.width,
            stroke_opacity=self.stroke_opacity
        )

        trace.add(new_line)

        self.sum_of_trace_lines_not_faded_out += np.linalg.norm(new_line.get_vector(), 2)
        self.sum_of_all_trace_lines += np.linalg.norm(new_line.get_vector(), 2)

        trace_length = len(trace.submobjects)

        non_faded_out_trace_length = trace_length if self.first_index_not_to_fade_out is None else len(trace.submobjects[self.first_index_not_to_fade_out:])
        should_fade_out_something = self.sum_of_all_trace_lines >= self.amount_to_not_fade_out_trace_before or non_faded_out_trace_length > self.max_number_of_trace_lines

        if self.first_index_not_to_fade_out is None:
            if non_faded_out_trace_length > self.max_number_of_trace_lines:
                self.first_index_not_to_fade_out = 1

            partial_sum_of_trace_line_lengths = 0
            for i in range(1, trace_length + 1):
                partial_sum_of_trace_line_lengths += np.linalg.norm(trace.submobjects[-i].get_vector(), 2)
                if partial_sum_of_trace_line_lengths > self.amount_to_not_fade_out_trace_before:
                    self.first_index_not_to_fade_out = trace_length - i
                    self.sum_of_trace_lines_not_faded_out = partial_sum_of_trace_line_lengths
                    break
        else:
            if self.sum_of_trace_lines_not_faded_out >= self.amount_to_not_fade_out_trace_before or non_faded_out_trace_length > self.max_number_of_trace_lines:
                if self.sum_of_trace_lines_not_faded_out < self.amount_to_not_fade_out_trace_before:
                    self.first_index_not_to_fade_out += 1
                else:
                    a = self.sum_of_trace_lines_not_faded_out
                    found_value = False
                    for i in range(1, trace_length - self.first_index_not_to_fade_out + 1):
                        if a - sum(np.linalg.norm(trace.submobjects[j].get_vector(),2)
                            for j in range(self.first_index_not_to_fade_out, self.first_index_not_to_fade_out + i)
                        ) <= self.amount_to_not_fade_out_trace_before:
                            found_value = True
                            self.first_index_not_to_fade_out += i
                            break
                    if not found_value:
                        if non_faded_out_trace_length > self.max_number_of_trace_lines:
                            self.first_index_not_to_fade_out += 1
                        else:
                            self.first_index_not_to_fade_out = trace_length - 1
            else:
                pass
            self.sum_of_trace_lines_not_faded_out = sum(np.linalg.norm(line.get_vector(), 2) for line in trace.submobjects[self.first_index_not_to_fade_out:])
            self.sum_of_all_trace_lines = sum(np.linalg.norm(line.get_vector(), 2) for line in trace.submobjects)

        if self.first_index_not_to_fade_out is not None and should_fade_out_something:
            for index in range(self.first_index_not_to_fade_out-1, -1, -1):
                opacity = trace.submobjects[index].get_opacity()
                if opacity <= 2 * self.trace_fadeout_decrease_factor:
                    trace.submobjects[index].set_opacity(0)
                    self.trace.submobjects = self.trace.submobjects[index+1:]
                    self.first_index_not_to_fade_out -= index+1
                    break
                else:
                    trace.submobjects[index].set_opacity(
                        max(0, opacity - self.trace_fadeout_decrease_factor)
                    )
                    trace.submobjects[index].set_stroke(
                        width=trace.submobjects[index].get_stroke_width() * (1 - self.trace_fadeout_decrease_factor)
                    )

    def add_corners_to_trace(self, trace, coords):
        trace.add_points_as_corners([self.get_np_array_from_list(coords)])

    def update_trace(self, trace, coords, last_coords):
        (self.trace_update_function)(trace, coords, last_coords)


    def get_trace_color(self):
        if self.color_code_velocity:
            vec = self.get_np_array_from_list(self.apply_functions_to_point(self.coords))
            val = np.linalg.norm(vec, 2)
            for color, limit in self.color_mappings:
                if val > limit:
                    return color
        elif self.fade_out_trace:
            return self.color

    def copy_coords(self, vec1, vec2):
        """Copies values of vec2 into vec1."""

        for i in range(len(vec2)):
            vec1[i] = vec2[i]

        return vec1


    def get_np_array_from_list(self, point):
        """Takes a point in the form of a list with two or three elements
        and returns a np.array with the point in question."""

        return np.array(np.array(self.adapt_dimensions(point)))


    def get_list_from_np_array(self, point):
        """Takes a point in the form of a np.array and returns 
        a list with the point in the correct dimension."""

        return list(point)[:self.dimension]


    def adapt_dimensions(self, point):
        """Takes a list and indexes two or three elemnts of it according to the system's dimension."""
        return [point[0], point[1], point[2] if self.dimension == 3 else 0]


    def update_coord(self, coords, dt, axis):
        return coords[axis] + self.functions[axis](*coords) * dt * self.speed_rate


    def update_coords(self, coords, dt):
        for axis in self.dimension_axes:
            coords[axis] = self.update_coord(coords, dt, axis)
        return coords


    def apply_functions_to_point(self, point):
        """Applies the system functions to a point (either a np.array or list)."""
        if isinstance(point, np.ndarray):
            return np.array([
                self.functions[Coords.X](*self.get_list_from_np_array(point)),
                self.functions[Coords.Y](*self.get_list_from_np_array(point)),
                self.functions[Coords.Z](*self.get_list_from_np_array(point)) if self.dimension == 3 else 0
            ])
        else:
            return [self.functions[i](*point) for i in range(len(point))]

    
    def build_solution(self):
        """Builds the dynamical system in question.
        To be overridden in subclass."""

        pass


    def add_local_section(self, is_flow_box=False):
        """Adds a local section (or flow box) to the system.
        To be overridden in subclass."""

        pass


    def set_color(self, color):
        self.submobjects[0].stroke_color = color
        self.color = color.hex


    def set_style(self, style):
        if isinstance(style, DynamicalSystemStyle):
            self.__dict__.update(style.as_dict())
        else: # Assume it's a dictionary
            self.__dict__.update(style)


    def _calculate_local_section_or_flow_box(self, point, is_flow_box):
        # TODO: Make it so this stops relying so heavily on d_list. Maybe add class attributes for their cords instead.
        pos = self.get_np_array_from_list(point)
        
        # Tangent, perpendicular and normalized perpendicular vectors to the position
        tangent_vector = self.apply_functions_to_point(pos)
        perp_vector = self.get_np_array_from_list([-tangent_vector[1],tangent_vector[0]])
        norm_perp_vector = normalize(perp_vector) * 0.5

        # Axis and center of the local section
        section_color = self.flow_box_perp_vector_color if is_flow_box else self.local_section_perp_vector_color
        line_start = pos - norm_perp_vector
        line_end = pos + norm_perp_vector
        section_perp_line = Line(
            start=line_start, 
            end=line_end,
            color=section_color
        )
        line_start_tip = Dot(line_start, color=section_color, radius=0.035)
        line_end_tip = Dot(line_end, color=section_color, radius=0.035)
        section_perp_line = VGroup(section_perp_line, line_start_tip, line_end_tip)
        section_center = Dot(pos, radius=self.point_radius, color=self.local_section_vector_color)

        # Number of vectors to draw for each orientation (up, down), and the vectors (anchors) in question
        vec_freq = self.local_section_vec_freq
        anchors = [
            pos + norm_perp_vector - i * norm_perp_vector
            for i in np.arange(0, 2 + 1/vec_freq, 1/vec_freq)
        ]
        solutions = []
        if is_flow_box:
            # Coords of points of the left and right sides of the flow box, respectively
            flow_box_side_points = [[], []]
            # Actual sides to return
            flow_box_sides = []

            for vec in anchors:
                direction = normalize(self.apply_functions_to_point(vec)) * 0.7
                solution = self.get_solution_through_point(vec)
                solutions.append(solution.trace)
                flow_box_side_points[0].append(solution.extreme_point_backward)
                flow_box_side_points[1].append(solution.extreme_point_forward)

            for i in [0,1]:
                flow_box_sides += [
                    Circle(
                        radius=0,
                        stroke_color=self.flow_box_trace_color,
                    ).move_to(flow_box_side_points[i][0])
                ]
                flow_box_sides[i].set_points_as_corners(flow_box_side_points[i])

            # Group section center with box sides for convenience
            section_center = VGroup(section_center, *flow_box_sides)
        else:
            for vec in anchors + [pos]:
                direction = normalize(self.apply_functions_to_point(vec)) * 0.7
                solutions.append(Line(
                    start=vec,
                    end=vec + direction,
                    color=self.local_section_vector_color
                ).add_tip(length=0.1, width=0.1))

        local_section = VGroup(*solutions, section_perp_line, section_center)
        return local_section
    

    def get_solution_through_point(self, point):
        raise Exception("Need to implement get_solution_through_point in a subclass.")




class SystemColorManager:
    def setup_color_mappings(self, dynamical_system: BaseDynamicalSystem) -> None:
        if dynamical_system.color_code_velocity:
            assert len(dynamical_system.velocity_colors) == 3, "Must take exactly three colors for coloring velocity"
            
            slow_to_med_color_weight = 1
            # A few ways of automatically generating the color code limit, i.e. the value
            # after which lines are painted in the color associated ot the highest velocity.
            if dynamical_system.color_code_velocity == 'from_trace':
                color_coding_limit = self._get_color_coding_limit_from_trace_simulation(dynamical_system) 
            elif dynamical_system.color_code_velocity == 'from_plane':
                color_coding_limit = self._get_color_coding_limit_from_plane_points(dynamical_system) 
            elif dynamical_system.color_code_velocity == 'manual':
                color_coding_limit = dynamical_system.velocity_colors[2][1]
                # slow_to_med_color_weight should be the percentage of the color coding limit
                # over which to calculate the slow_to_med gradient (higher percentage means
                # higher thresholds for slow color)
                slow_to_med_color_weight = dynamical_system.velocity_colors[0][1]
            else:
                raise AssertionError("Unsupported color_code_velocity type")
            
            dynamical_system.velocity_colors = [Color(c[0]) for c in dynamical_system.velocity_colors]
            color_slow_to_med = list(dynamical_system.velocity_colors[0].range_to(dynamical_system.velocity_colors[1], DS_COLOR_CODING_VARIETY))
            color_med_to_fast = list(dynamical_system.velocity_colors[1].range_to(dynamical_system.velocity_colors[2], DS_COLOR_CODING_VARIETY))
            colors = color_slow_to_med + color_med_to_fast[1:]

            if slow_to_med_color_weight == 1:
                step = color_coding_limit / len(colors)           
                value_range = np.arange(0, color_coding_limit + step/2, step)
            else:
                weighted_half_color_coding_limit = slow_to_med_color_weight*color_coding_limit
                slow_to_med_step = weighted_half_color_coding_limit / (len(color_slow_to_med) - 1)
                med_to_fast_step = (color_coding_limit - weighted_half_color_coding_limit) / len(color_med_to_fast)
                slow_to_med_values = list(np.arange(0, weighted_half_color_coding_limit + slow_to_med_step/2, slow_to_med_step))[1:]
                med_to_fast_values = list(np.arange(weighted_half_color_coding_limit + med_to_fast_step, color_coding_limit + med_to_fast_step/2, med_to_fast_step))
                value_range = slow_to_med_values + med_to_fast_values

            dynamical_system.color_mappings = list(zip(colors, value_range))
            dynamical_system.color_mappings.reverse()

    def _get_color_coding_limit_from_trace_simulation(self, dynamical_system: BaseDynamicalSystem):
        """Generates a color coding limit by iteratively updating the system's
        coordinates and using the maximum of all calculated coordinates.."""

        initial_coords = copy.deepcopy(dynamical_system.coords)
        color_coding_limit = max(
            np.linalg.norm(
                dynamical_system.update_coords(initial_coords, HD_TIME_DELTA), 2
            ) for _ in range(DS_TRACE_COLOR_CODING_N_OF_ITERATIONS)
        ) * DS_COLOR_CODING_SCALE_FACTOR

        # Equilibrium points would result in a color coding limit of 0,
        # which we can't have currently
        return color_coding_limit if color_coding_limit > 0 else 0.01

    def _get_color_coding_limit_from_plane_points(self, dynamical_system: BaseDynamicalSystem):
        """Generates a color coding limit by applying the system functions once
        to a bunch of integer pairs of the plane and getting the maximum among
        those values."""

        rg_vals = [-DS_PLANE_COLOR_CODING_VALUES_RANGE, DS_PLANE_COLOR_CODING_VALUES_RANGE]
        if dynamical_system.dimension == 3:
            return max(
                np.linalg.norm(
                    dynamical_system.apply_functions_to_point([x, y, z]), 2
                ) for x in range(*rg_vals) for y in range(*rg_vals) for z in range(*rg_vals)
            ) * DS_COLOR_CODING_SCALE_FACTOR
        else:
            return max(
                np.linalg.norm(
                    dynamical_system.apply_functions_to_point([x, y]), 2
                ) for x in range(*rg_vals) for y in range(*rg_vals)
            ) * DS_COLOR_CODING_SCALE_FACTOR