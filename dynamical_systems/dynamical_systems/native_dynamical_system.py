from manimlib import *
from dynamical_systems import *
import numpy as np
import math
from colour import Color
from collections import Counter


# TODO: build system snapshot inside animated lines class
# TODO: handle properly fades and make it optional
# TODO: revise comments
# TODO: Handle multiple systems


class NativeDynamicalSystemSnapshot(StreamLines):
    CONFIG = {
        # Time step used at each iteration
        "dt": DEFAULT_TIME_DELTA,
        # Max arc length the system can achieve
        "arc_len": 1e50,
        "stroke_width": 3.2,
        "point_radius": 0.05,
    }

    def __init__(
        self,
        initial_position: list[float] | list[list[float]],
        time_domain: list[float],
        func: Callable[[float, float], Sequence[float]],
        coordinate_system: CoordinateSystem,
        **kwargs
    ):
        assert len(time_domain) == 2, "Time domain should consist of two numbers"
        assert time_domain[0] <= time_domain[1], "Start time should not be larger than end time"

        if type(initial_position[0]) == float:
            assert len(initial_position) in [2, 3], f"Unsupported dimension: {len(initial_position)}"
            self.initial_position = [initial_position]
        else:
            pos_lens = set(len(p) for p in initial_position)
            assert all([p in [2, 3] for p in pos_lens]), f"Unsupported dimension: {pos_lens - {2, 3}}"
            self.initial_position = initial_position

        self.time_domain = time_domain

        self.max_time_steps = int(time_domain[1] / DEFAULT_TIME_DELTA)
        # The StreamLines code divides the total number of steps by
        # n_samples_per_line, and uses it as the step with which to take
        # anchor points, if its larger than 1. Setting it equal to the number
        # # of samples will ensure a step of 1, so all sampled points are anchor points
        self.n_samples_per_line = self.max_time_steps
        # Limits the norm of the dynamical system to the size of the coordinate system
        self.cutoff_norm = 10 * abs(max(coordinate_system.x_range[:2])) + abs(max(coordinate_system.y_range[:2]))

        super().__init__(func, coordinate_system, **kwargs)

        self.dot = self.get_dot()

    def draw_lines(self) -> None:
        lines = []
        self.dots = VGroup()
        origin = self.coordinate_system.get_origin()

        self.points = []
        self.cumulative_arc_lens = []
        self.arc_lens = []
        self._modified_arc_lens = []
        self._interpolation_values = []

        for i, point in enumerate(self.get_start_points()):
            points = [point]
            total_arc_len = 0
            time = 0
            self.arc_lens.append([])
            self.cumulative_arc_lens.append([0])

            for x in range(self.max_time_steps):
                time += self.dt
                last_point = points[-1]
                new_point = last_point + self.dt * (self.point_func(last_point) - origin)
                points.append(new_point)
                self.arc_lens[i].append(get_norm(new_point - last_point))
                total_arc_len += self.arc_lens[i][-1]
                self.cumulative_arc_lens[i].append(total_arc_len)
                if get_norm(last_point) > self.cutoff_norm:
                    break
                if total_arc_len > self.arc_len:
                    break
            line = VMobject()
            line.virtual_time = time
            step = max(1, int(len(points) / self.n_samples_per_line))
            line.set_points_as_corners(points[::step])
            line.make_approximately_smooth()
            lines.append(line)

            self.points.append(points[::step])
            line.anchor_points = points[::step]
            self._modified_arc_lens.append([self._modified_sigmoid(a) for a in self.arc_lens[i]])

        self._interpolation_values = [
                sum(self._modified_arc_lens[0][:i+1]) / sum(self._modified_arc_lens[0]) for i in range(self.max_time_steps)
            ]
        self.set_submobjects(lines)
    
    def get_dot(self) -> None:
        return Dot(
            point=self.submobjects[-1].data["points"][-1],
            radius=self.point_radius
        )

    def add_to_scene(self, scene: Scene) -> None:
        scene.add(self)
        scene.bring_to_front(self.dot)

    def get_start_points(self) -> np.ndarray:
        return [self.coordinate_system.c2p(*p) for p in self.initial_position]
    
    def _modified_sigmoid(self, t):
        return 2 * (1 - 1 / (1 + math.exp(-t)))
    

class DynamicalSystemAnimation(ShowPartial):
    CONFIG = {
        "time_width": 0.3,
        "taper_width": 0.02,
        "remover": True,
        "fade_start_time": DEFAULT_FADE_START_TIME,
        "fade": False
    }

    def __init__(
        self,
        mobject: Mobject,
        system: Callable[[float, float], Sequence[float]],
        **kwargs
    ) -> None:

        self.system = system
        super().__init__(mobject, **kwargs)

    # def draw_debug_time_mobjects(self):
    #     return VGroup(
    #         DecimalNumber(self.current_time),
    #         DecimalNumber(self.unmodified_cutoff_time),
    #         DecimalNumber(self.fade_start_time),
    #         DecimalNumber(self.current_cum_arc_len)
    #     ).arrange(DOWN).next_to(self.text)

    def begin(self) -> None:
        if self.fade:
            self.mobject.align_stroke_width_data_to_points()
            # Compute an array of stroke widths for each submobject
            # which tapers out at the beginning
            self.submob_to_anchor_widths = dict()
            for sm in self.mobject.get_family():
                original_widths = sm.get_stroke_widths()
                anchor_widths = np.array([*original_widths[0::3], original_widths[-1]])

                def taper_kernel(x):
                    if x < 1e-20:
                        return x
                    return 1.0

                taper_array = list(map(taper_kernel, np.linspace(0, 1, len(anchor_widths))))
                self.submob_to_anchor_widths[hash(sm)] = anchor_widths * taper_array
        
        super().begin()

        if not self.should_match_start:
            self.mobject.lock_matching_data(self.mobject, self.starting_mobject) 

    def finish(self) -> None:
        super().finish()
        self.mobject.unlock_data()

        if self.fade:
            for submob, start in self.get_all_families_zipped():
                submob.match_style(start)

    def interpolate_submobject(
        self,
        submob: VMobject,
        start_submob: VMobject,
        alpha: float
    ) -> None:
        submob.pointwise_become_partial(
            start_submob, *self.get_bounds(alpha)
        )

        if self.fade:
            self._maybe_fade_submobject(submob)

    def _maybe_fade_submobject(self, submob: VMobject) -> None:
        anchor_widths = self.submob_to_anchor_widths[hash(submob)]
        
        submob_points = submob.get_points()
        count = Counter([tuple(p) for p in submob_points])
        try:
            self.last_used_anchor = int(next(filter(lambda t: t > 2, count.values())) / 3)
        except StopIteration:
            self.last_used_anchor = 0

        # time of last shown point of the system
        current_time = float((len(anchor_widths) - self.last_used_anchor) * self.system.dt)
        # time before which to completely fade
        cutoff_time = current_time - self.fade_start_time - 3.0
        capped_cutoff_time = max(cutoff_time, 0)
        # time before which to start fading
        fade_start_time = max(current_time - self.fade_start_time, 0)

        def fade_kernel(i: int) -> float:
            # time of point being evaluated
            eval_time = i * self.system.dt

            if eval_time <= capped_cutoff_time:
                return 0
            if eval_time >= fade_start_time:
                return 1

            return (eval_time - cutoff_time * 1.05) / (fade_start_time - cutoff_time * 1.05)

        kernel_array = list(map(fade_kernel, range(len(submob.anchor_points))))

        scaled_widths = anchor_widths * kernel_array
        new_widths = np.zeros(submob.get_num_points())
        new_widths[0::3] = scaled_widths[:-1]
        new_widths[2::3] = scaled_widths[1:]
        new_widths[1::3] = (new_widths[0::3] + new_widths[2::3]) / 2
        submob.set_stroke(width=new_widths)

    def get_bounds(self, alpha: float) -> tuple[float, float]:
        return (0, alpha)


class NativeDynamicalSystem(AnimatedStreamLines):
    CONFIG = {
        "lag_range": 0,
        "line_anim_class": DynamicalSystemAnimation,
        "line_anim_config": dict()
    }

    def __init__(
            self,
            stream_lines: NativeDynamicalSystemSnapshot,
            speed_rate: float,
            # animation-related parameters
            fade: bool=False,
            fade_start_time: bool=DEFAULT_FADE_START_TIME,
            **kwargs
        ):

        self.speed_rate = speed_rate
        for line in stream_lines:
            line.virtual_time /= speed_rate

        self.CONFIG["line_anim_config"].update(dict(
            system=stream_lines,
            fade=fade,
            fade_start_time=fade_start_time
        ))
    
        super().__init__(stream_lines, **kwargs)

    def update(self, dt: float) -> None:
        for line in self.stream_lines:
            line.time += dt * self.speed_rate
            line.anim.update(line.time / line.anim.run_time)
            if line.time > line.anim.run_time:
                self.clear_updaters()

    def reset(self):
        for line in self.stream_lines:
            line.time = 0

        self.add_updater(lambda m, dt: m.update(dt))

    def add_to_scene(self, scene: Scene) -> None:
        scene.add(self)
