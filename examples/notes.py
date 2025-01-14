from manimlib import *
from dynamical_systems import *
import math


class TestColorCodedSystem(Scene):
    def construct(self):
        plane = NumberPlane()
        self.add(plane)

        time = 8

        initial_positions = [[1.2, 1.3]]

        lines = NativeDynamicalSystemSnapshot(
            func=lambda x, y: [
                math.sin(y) - 0.05*x,
                math.cos(x)
            ],
            # func=lambda x, y: [y, - 0.5 * y - 2* math.sin(x/2) + 0.5],
            coordinate_system=plane,
            initial_position=initial_positions,
            time_domain=[0, time]
        )

        animated_lines = NativeDynamicalSystem(
            speed_rate=1,
            stream_lines=lines,
            scene=self,
            fade_start_time=3,
            fade=True
        )

        animated_lines.add_to_scene(self)

        self.wait(time)