from manimlib import *
from dynamical_systems.constants import *



class DynamicalSystemStyle:
    VALID_ATTRS = [
        'speed_rate',
        'color',
        'width',
        'stroke_opacity',
        'point_radius',
        'point_color',
        'local_section_perp_vector_color',
        'local_section_vector_color',
        'local_section_vec_freq',
        'flow_box_perp_vector_color',
        'flow_box_trace_color',
        'flow_box_trace_width',
        'flow_box_solution_time_domain',
        'velocity_colors',
        'trace_fadeout_decrease_factor',
        'amount_to_not_fade_out_trace_before',
        'line_trace_overlap_buff',
        'max_number_of_trace_lines',
        'precision_multiplier_if_trace_too_rough',
        'trace_precision_increase_threshold'
    ]

    def __init__(self, **kwargs):
        self._init_traits()
        for trait, value in kwargs.items():            
            if trait not in self.VALID_ATTRS:
                raise Exception(f'Unsupported style attribute: {trait}')
            self.__dict__[trait] = value

    def _init_traits(self):
        for trait in self.VALID_ATTRS:
            self.set_value(trait, None)

    def as_dict(self):
        return {trait: self.get_value(trait) for trait in self.VALID_ATTRS}
    
    def get_value(self, trait):
        return self.__dict__[trait]

    def set_value(self, trait, value):
        self.__dict__[trait] = value

    @classmethod
    def from_existing_style(cls, dynamical_system_style, **kwargs):
        new_style = dynamical_system_style.as_dict()
        new_style.update(kwargs)
        return cls(**new_style)

    def __str__(self):
        return str(self.as_dict())



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
    line_trace_overlap_buff=EXP_SCENE_DEFAULT_TRACE_OVERLAP_BUFF,
    max_number_of_trace_lines=500,
    # [int] How many times to split dt in a single frame to add more steps to the approximation.
    # Increase to add detail and preserve speed rate, or if there is a large variation in speed in the system.
    precision_multiplier_if_trace_too_rough=1,
    trace_precision_increase_threshold=0.15,
)

PHASE_PLANE_STYLE = DynamicalSystemStyle.from_existing_style(
    BASE_STYLE,
    point_radius=0.035,
    width=2.8,
    stroke_opacity=0.65
)