from manimlib import *
import numpy as np
import math
import copy
from enum import IntEnum
from typing import List
from colour import Color
import random


UHD_TIME_DELTA = 0.00666666666666666
HD_TIME_DELTA =  0.01666666666666572
SD_TIME_DELTA  = 0.06666666666666666
VERY_LOW_QUALITY_TIME_DELTA  = 0.15
DEFAULT_TIME_DELTA = HD_TIME_DELTA

DEFAULT_TIME_DOMAIN = [-10, 10]

DEFAULT_PHASE_PLANE_STEP = 1

COLOR_CODING_VARIETY = 20
COLOR_CODING_LIMIT = 30
COLOR_CODING_SCALE_FACTOR = 0.93

# TRACE_FADEOUT_DECREASE_FACTOR = 0.2
LINE_TRACE_OVERLAP_BUFF = 0.02
# LINE_TRACE_AMOUNT_TO_NOT_FADE_OUT = 0

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



class Coords(IntEnum):
    X = 0
    Y = 1
    Z = 2


class DynamicalSystemStyle:
    def __init__(self, **kwargs):
        self.style = kwargs
    
    @classmethod
    def from_existing_style(cls, dynamical_system_style, **kwargs):
        new_style = copy.deepcopy(dynamical_system_style.style)
        new_style.update(kwargs)
        return cls(**new_style)

    def __str__(self):
        return str(self.style)


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

# TODO: implement using coords_to_point when showing phase planes
# TODO: bifurcations
# TODO: stop using python lists and np.arrays at the same time
# TODO: Remove DynamicalSystemStyle class in favor of dicts




class PointAndTrace:
    def __init__(self, point, trace, **kwargs):
        # super().__init__(**kwargs)
        # self.add(trace, point)
        self.point = point
        self.trace = trace

    # @property
    # def trace(self):
    #     return self.submobjects[0]

    # @property
    # def point(self):
    #     return self.submobjects[1]



class BaseDynamicalSystemClass(VGroup):
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
        style=BASE_STYLE, 
        **kwargs
    ):
        self.__dict__.update(style.style) # Bundle style parameters into a 'style' attribute
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
        # TODO: Implement this for snapshots
        self.is_updated_coord_too_far = False
        self.second_to_last_coords = [copy.deepcopy(list(init_pos)) for _ in range(self.precision_multiplier_if_trace_too_rough - 1)]

        self.color_code_velocity = color_code_velocity
        self.fade_out_trace = fade_out_trace
        if fade_out_trace:
            self.sum_of_trace_line_lengths = 0
            self.first_index_not_to_fade_out = None
            self.sum_of_all_trace_lines = 0
            self.sum_of_trace_lines_not_faded_out = 0

        if color_code_velocity:
            assert len(self.velocity_colors) == 3, "Must take exactly three colors for coloring velocity"

            slow_to_med_color_weight = 1
            # Two ways of generating the color code limit, i.e. the value after which
            # lines are painted in the last color.
            # TODO: update comments to include manual color coding
            if color_code_velocity == 'from_trace':
                # This way simulates updates to the system a bunch of times
                # and uses the maximum of all those values to calculate the limit
                foo = copy.deepcopy(self.coords)
                color_coding_limit = max(
                    np.linalg.norm(
                        self.update_coords(foo, HD_TIME_DELTA), 2
                    ) for _ in range(200)
                ) * COLOR_CODING_SCALE_FACTOR
                # Equilibrium points would result in 0 limit, which would break this
                color_coding_limit = 0.01 if color_coding_limit == 0 else color_coding_limit    
            elif color_code_velocity == 'from_plane':
                # This way applies the system functions to a bunch of integer pairs 
                # and uses the maximum of those values to calculate the limit
                # Comenting out for now
                rg_vals = [-10,10]
                if self.dimension == 3:
                    color_coding_limit = max(
                        np.linalg.norm(
                            self.apply_functions_to_point([x, y, z]), 2
                        ) for x in range(*rg_vals) for y in range(*rg_vals) for z in range(*rg_vals)
                    ) * COLOR_CODING_SCALE_FACTOR
                else:
                    color_coding_limit = max(
                        np.linalg.norm(
                            self.apply_functions_to_point([x, y]), 2
                        ) for x in range(*rg_vals) for y in range(*rg_vals)
                    ) * COLOR_CODING_SCALE_FACTOR
            elif color_code_velocity == 'manual':
                color_coding_limit = self.velocity_colors[2][1]
                # slow_to_med_color_weight should be the percentage of the color coding limit
                # over which to calculate the slow_to_med gradient (higher percentage means
                # higher thresholds for slow color)
                slow_to_med_color_weight = self.velocity_colors[0][1]
            else:
                raise AssertionError("unsupported color_code_velocity type")
            
            self.velocity_colors = [Color(c[0]) for c in self.velocity_colors]
            # color_slow_to_med = list(self.velocity_colors[0].range_to(self.velocity_colors[1], COLOR_CODING_VARIETY + math.floor(slow_to_med_color_weight*COLOR_CODING_VARIETY)))
            # color_med_to_fast = list(self.velocity_colors[1].range_to(self.velocity_colors[2], COLOR_CODING_VARIETY - math.floor(slow_to_med_color_weight*COLOR_CODING_VARIETY)))
            color_slow_to_med = list(self.velocity_colors[0].range_to(self.velocity_colors[1], COLOR_CODING_VARIETY))
            color_med_to_fast = list(self.velocity_colors[1].range_to(self.velocity_colors[2], COLOR_CODING_VARIETY))
            colors = color_slow_to_med + color_med_to_fast[1:]

            if slow_to_med_color_weight == 0:
                step = color_coding_limit / len(colors)           
                value_range = np.arange(0, color_coding_limit + step/2, step)
            else:
                weighted_half_color_coding_limit = slow_to_med_color_weight*color_coding_limit
                slow_to_med_step = weighted_half_color_coding_limit / (len(color_slow_to_med) - 1)
                med_to_fast_step = (color_coding_limit - weighted_half_color_coding_limit) / len(color_med_to_fast)
                slow_to_med_values = list(np.arange(0, weighted_half_color_coding_limit + slow_to_med_step/2, slow_to_med_step))[1:]
                med_to_fast_values = list(np.arange(weighted_half_color_coding_limit + med_to_fast_step, color_coding_limit + med_to_fast_step/2, med_to_fast_step))
                value_range = slow_to_med_values + med_to_fast_values

            self.color_mappings = list(zip(colors, value_range))
            self.color_mappings.reverse()


        # self.unused_traces_repository = [Line(stroke_opacity=0, fill_opacity=0) for _ in range(300)]
        # self.scene.add(*(self.unused_traces_repository))
        point = SurfaceMesh(Sphere(), resolution=(10, 10), color=self.point_color).scale(self.point_radius).move_to(self.init_pos_vector)
        # point = Dot(radius=self.point_radius).move_to(self.init_pos_vector)#, radius=self.point_radius)

        # TODO: See if high mesh resolution affects render time severely
        
        trace = self.get_base_trace(color_code_velocity)
        self.point_and_trace = PointAndTrace(point, trace)
        self.trace_update_function = self.get_trace_update_function()
        self.unused_traces_repository = []

        self.build_solution()

        super().__init__(self.point_and_trace.trace, self.point_and_trace.point)


    def add_to_scene(self):
        # self.scene.add(self.point_and_trace)
        self.scene.add(self.point_and_trace.point, self.point_and_trace.trace)
        self.scene.bring_to_front(self.point_and_trace.trace)
        # self.scene.bring_to_front(self.point_and_trace.point)

        if not self.show_point:
            self.point_and_trace.point.set_opacity(0)

    def remove_from_scene(self):
        self.scene.remove(self.point_and_trace.point, self.point_and_trace.trace)


    def get_base_trace(self, color_code_velocity=False):
        parameters = dict(
            stroke_color=self.color,
            stroke_width=self.width,
            stroke_opacity=self.stroke_opacity
        )

        if color_code_velocity:
            trace = VGroup(**parameters)
        else:
            trace = Circle(
                radius=0,
                **parameters
            )

        return trace.move_to(self.init_pos_vector)

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
        trace.refresh_has_updater_status()
        trace.refresh_bounding_box()

        # trace.family[1] = it.chain(trace.family[1], [new_line])
        # trace.family = [trace] + trace.submobjects
        # print(len(trace.family), trace.family[:3])
        # trace.assemble_family()
        # trace.add(new_line)

    def add_line_objects_to_trace_and_fade_out(self, trace, coords, last_coords):
        # Assuming trace is a VGroup object
        new_position = self.get_new_line_position(coords, last_coords)
        if self.unused_traces_repository:
            color = np.array([color_to_rgb(self.get_trace_color())])
            new_line = self.unused_traces_repository.pop(0).set_points_as_corners(
                [new_position[0], new_position[1]]
            )
            new_line.data['fill_rgba'][:, :3] = color # Set color to fill
            new_line.data['fill_rgba'][:, 3] = 1 # Set opacity to fill
            new_line.data['stroke_rgba'][:, :3] = color # Set color to stroke
            new_line.data['stroke_rgba'][:, 3] = 1 # Set opacity to stroke
            new_line.data['stroke_width'] = np.array([[float(self.width)]])


            # new_line = self.unused_traces_repository.pop(0).set_points_by_ends(
            #     new_position[0], 
            #     new_position[1]
            # ).set_fill(
            #     opacity=1,
            #     color=self.get_trace_color(),
            # ).set_stroke(
            #     opacity=1,
            #     width=self.width,
            #     color=self.get_trace_color()
            # )

            #set_opacity(1)#.set_stroke(width=self.width)#.set_color(self.get_trace_color())
            # new_line.stroke_width = self.width
            # new_line.color = self.get_trace_color()
            # new_line.opacity = 1

        else:
            new_line = Line(
                new_position[0],
                new_position[1],
                color=self.get_trace_color(),
                stroke_width=self.width,
                stroke_opacity=self.stroke_opacity
            )
            # self.scene.add(new_line)
            # print('      > added new line')


        # current_time = time.process_time()
        current_time = time.process_time()

        trace.add(new_line)

        # trace.submobjects.append(new_line)
        # trace.family.insert(0, new_line)
        # trace.refresh_has_updater_status()
        # trace.refresh_bounding_box()

        # time_to_add_trace = time.process_time() - current_time
        # print('\n')
        # print("Sum of lengths:", round(self.sum_of_trace_lines_not_faded_out, 3), "First index not fadeout:", self.first_index_not_to_fade_out, "Trace length:", len(trace.submobjects))
        self.sum_of_trace_lines_not_faded_out += np.linalg.norm(new_line.get_vector(), 2)
        self.sum_of_all_trace_lines += np.linalg.norm(new_line.get_vector(), 2)
        # print("New sum of trace lenghts:", self.sum_of_trace_lines_not_faded_out)

        trace_length = len(trace.submobjects)
        # print("trace length", trace_length)
        # print('Length of new line:', np.linalg.norm(new_line.get_vector(), 2))
        non_faded_out_trace_length = trace_length if self.first_index_not_to_fade_out is None else len(trace.submobjects[self.first_index_not_to_fade_out:])

        should_fade_out_something = self.sum_of_all_trace_lines >= self.amount_to_not_fade_out_trace_before or non_faded_out_trace_length > self.max_number_of_trace_lines

        # print("\nis over threshold?", self.sum_of_trace_lines_not_faded_out >= self.amount_to_not_fade_out_trace_before, f" (sum of trace lengths: {self.sum_of_trace_lines_not_faded_out})")
        # print("is length too long?", non_faded_out_trace_length > self.max_number_of_trace_lines, f" (length: {non_faded_out_trace_length})")
        # print("first_index_not_to_fade_out is: ", self.first_index_not_to_fade_out)
        # print("total length:", sum(np.linalg.norm(line.get_vector(), 2) for line in trace.submobjects))
        # print("should fade out something:", should_fade_out_something)

        # if non_faded_out_trace_length > self.max_number_of_trace_lines:
        #     # self.first_index_not_to_fade_out = trace_length - self.max_number_of_trace_lines
        #     if self.first_index_not_to_fade_out is None:
        #         self.first_index_not_to_fade_out = 0
        #     else:
        #         self.first_index_not_to_fade_out += 1
        #     print("TRACE_LENGTH EXCEEDED - new first-index-not-to:", self.first_index_not_to_fade_out, non_faded_out_trace_length)
        if self.first_index_not_to_fade_out is None:
            # print("first_index_not_to_fade_out is None for now")
            if non_faded_out_trace_length > self.max_number_of_trace_lines:
                self.first_index_not_to_fade_out = 1

            partial_sum_of_trace_line_lengths = 0
            for i in range(1, trace_length + 1):
                partial_sum_of_trace_line_lengths += np.linalg.norm(trace.submobjects[-i].get_vector(), 2)
                if partial_sum_of_trace_line_lengths > self.amount_to_not_fade_out_trace_before:
                    # print("Found a first_index_not_to_fade_out")
                    self.first_index_not_to_fade_out = trace_length - i
                    self.sum_of_trace_lines_not_faded_out = partial_sum_of_trace_line_lengths
                    break
        else:
            # print("first_index_not_to_fade_out is NOT None - and is", self.first_index_not_to_fade_out)
            if self.sum_of_trace_lines_not_faded_out >= self.amount_to_not_fade_out_trace_before or non_faded_out_trace_length > self.max_number_of_trace_lines:
                # print("New line causes to exceed fadeout threshold")
                if self.sum_of_trace_lines_not_faded_out < self.amount_to_not_fade_out_trace_before:
                    self.first_index_not_to_fade_out += 1
                else:
                    a = self.sum_of_trace_lines_not_faded_out
                    found_value = False
                    for i in range(1, trace_length - self.first_index_not_to_fade_out + 1):
                        # print("---- Checking where to increase first_index_not_to_fade_out - currently on", self.first_index_not_to_fade_out + i - 1)
                        # print("     > length of this line:", np.linalg.norm(trace.submobjects[self.first_index_not_to_fade_out + i - 1].get_vector(),2))
                        # print("     > sum up to this vector:", a - sum(np.linalg.norm(trace.submobjects[j].get_vector(),2) for j in range(self.first_index_not_to_fade_out, self.first_index_not_to_fade_out + i)))
                        if a - sum(np.linalg.norm(trace.submobjects[j].get_vector(),2)
                            for j in range(self.first_index_not_to_fade_out, self.first_index_not_to_fade_out + i)
                        ) <= self.amount_to_not_fade_out_trace_before:
                            found_value = True
                            self.first_index_not_to_fade_out += i
                            # print("first_index_not_to_fade_out increased by", i, " - now is", self.first_index_not_to_fade_out)
                            break
                        # elif self.first_index_not_to_fade_out + i > self.max_number_of_trace_lines:
                        #     found_value = True
                        #     self.first_index_not_to_fade_out += i
                        #     print(f"Trace too long! {trace_length=}, first_index_not_to_fade_out={self.first_index_not_to_fade_out}")
                        # else:
                            # self.sum_of_trace_lines_not_faded_out -= np.linalg.norm(trace.submobjects[self.first_index_not_to_fade_out + i - 1].get_vector(),2)
                    if not found_value:
                        # print("Last value alone is bigger than threshold?")
                        if non_faded_out_trace_length > self.max_number_of_trace_lines:
                            self.first_index_not_to_fade_out += 1
                            print("TRACE_LENGTH EXCEEDED - new first-index-not-to:", self.first_index_not_to_fade_out, non_faded_out_trace_length)
                        else:
                            self.first_index_not_to_fade_out = trace_length - 1
            else:
                # self.first_index_not_to_fade_out = 0
                # print("Sum of trace lengths NOT BIGGER THAN THRESHOLD")
                pass
            self.sum_of_trace_lines_not_faded_out = sum(np.linalg.norm(line.get_vector(), 2) for line in trace.submobjects[self.first_index_not_to_fade_out:])
            self.sum_of_all_trace_lines = sum(np.linalg.norm(line.get_vector(), 2) for line in trace.submobjects)

        
        if self.first_index_not_to_fade_out is not None and should_fade_out_something:
            # print("Iterating through lines to see which ones to fade out completely...")
            for i in range(1, self.first_index_not_to_fade_out + 1):
                index = self.first_index_not_to_fade_out - i
                opacity = trace.submobjects[index].get_opacity()
                if opacity <= self.trace_fadeout_decrease_factor:
                    # print("Will delete everything before line", index)
                    trace.submobjects[index].set_opacity(0)
                    self.unused_traces_repository += self.point_and_trace.trace.submobjects[:index+1]
                    self.point_and_trace.trace.submobjects = self.point_and_trace.trace.submobjects[index+1:]
                    self.first_index_not_to_fade_out -= index
                    break
                else:
                    # print("Faded out a bit line", index)
                    trace.submobjects[index].set_opacity(
                        max(0, opacity - self.trace_fadeout_decrease_factor)
                    )
                    trace.submobjects[index].set_stroke(
                        width=trace.submobjects[index].get_stroke_width() * (1 - self.trace_fadeout_decrease_factor)
                    )

        # print(f"Time to add trace: {time_to_add_trace}")
        # print(f"Time to calc. ind: {time.process_time() - time_to_add_trace - current_time}")
        # print(f"       Total time: {time.process_time() - current_time}\n")


    def add_corners_to_trace(self, trace, coords):
        trace.add_points_as_corners([self.get_np_array_from_list(coords)])

    def update_trace(self, trace, coords, last_coords):
        (self.trace_update_function)(trace, coords, last_coords)


    def get_trace_color(self):
        if self.color_code_velocity:
            vec = self.get_np_array_from_list(self.apply_functions_to_point(self.coords))
            val = np.linalg.norm(vec, 2)
            # print(val)
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
        # print(axis, " ---- ", self.functions[axis](*coords))
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
            self.__dict__.update(style.style)
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
        section_center = Dot(pos, radius=self.point_and_trace.point_radius, color=self.local_section_vector_color)

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



class DynamicalSystemSnapshot(BaseDynamicalSystemClass):
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

        self.trace = VGroup(self.point_and_trace.trace, self.backward_trace, self.forward_trace)
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
            ) > 0.15

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
            # self.scene.bring_to_front(self.point_and_trace.trace)


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

        self.point_and_trace.trace = VGroup(self.point_and_trace.trace, self.backward_trace, self.forward_trace)
        self.point_and_trace.point.move_to(self.extreme_point_forward)


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
            self.point_and_trace.point.set_opacity(0)

    def remove_from_scene(self):
        self.scene.remove(self.trace, self.point)




class DynamicalSystem(BaseDynamicalSystemClass):
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
        self.point_and_trace_func = self.get_point_and_trace

        super().__init__(scene, init_pos, dx, dy, dz, show_point, color_code_velocity, fade_out_trace, style, **kwargs)


    def get_point(self, point, dt):
        """Updates coordinates of the system's point."""

        maybe_updated_coords = self.update_coords(copy.deepcopy(self.coords), dt)
        self.is_updated_coord_too_far = np.linalg.norm(
            self.get_np_array_from_list(maybe_updated_coords) - self.get_np_array_from_list(self.last_coords),
            2
        ) > 0.15

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
        self.scene.bring_to_front(self.point_and_trace.trace)

        # print("Trace updated - moved to", [round(c, 7) for c in self.coords], "from", [round(c, 7) for c in self.last_coords], '\n')
            
    def get_point_and_trace(self, point_and_trace, dt):
        # print(len(self.point_and_trace.trace.submobjects))
        if dt > 0.2:
            dt = 0
        new_point = self.get_point(point_and_trace.point, dt)
        self.get_trace(point_and_trace.trace)
        return PointAndTrace(new_point, point_and_trace.trace)


    def build_solution(self):
        # self.point_and_trace.add_updater(self.point_and_trace_func)
        self.point_and_trace.point.add_updater(self.get_point_func)
        self.point_and_trace.trace.add_updater(self.get_trace_func)


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
        time_domain=DEFAULT_TIME_DOMAIN,
        show_snapshots=False, # Whether to show a DynamicalSystemSnapshot (True) or DynamicalSystem (False)
        show_points=True,
        color_code_velocity=False,
        fade_out_trace=False,
        lower_quality=False,
        style=BASE_STYLE,
        color=BASE_STYLE.style['color'], # can either be a single color or a list of colors to fade
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
                    solution.build_solution_with_time_delta(VERY_LOW_QUALITY_TIME_DELTA)
            else:
                solution = DynamicalSystem(**parameters)
            self.systems.append(solution)

        if should_log_build_progress:
            print("Done!")

    def add_to_scene(self):
        for system in self.systems:
            system.add_to_scene()


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
        time_domain=DEFAULT_TIME_DOMAIN,
        show_snapshots=False, # Whether to show DynamicalSystemSnapshot's (True) or DynamicalSystem's (False)
        show_points=True,
        color_code_velocity=False,
        lower_quality=False,
        style=BASE_STYLE,
        **kwargs
    ):
        self.show_points = show_points
        step = DEFAULT_PHASE_PLANE_STEP
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
        time_domain=[0, DEFAULT_TIME_DOMAIN[1]],
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
