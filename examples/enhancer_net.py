import random
import numpy as np

from scipy.special import softmax

from manimlib import *

# Some tinkering may be needed to get this working - maybe adding the module folder to PYTHONPATH
from dynamical_systems import *


random.seed(0)


class EnhancerNetScene(ThreeDScene):
    """Simulates a simple EnhancerNet example with three-dimensional TF expressions."""

    # Helper method to configure and add axes
    def set_up_axes(self):
        axes = ThreeDAxes(
            x_range=[-20, 20],
            y_range=[-20, 20],
            z_range=[-20, 20],
        )
        self.add(axes)
        
        r1 = Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.camera.frame.set_orientation(rot)
        self.begin_ambient_camera_rotation(rate=0.0125)

    # Helper method to continuously rotate the camera
    def begin_ambient_camera_rotation(self, rate=0.003):
        self.camera.frame.add_updater(lambda camFrame: camFrame.rotate(angle=rate))

    # Helper method to calculate the cosine similarity of vectors
    def cosine_similarity(self, a, b):
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)

    # This is where the magic happens
    def construct(self):
        self.set_up_axes()

        # Define enhancer matrix and normalize it
        Xi_unnormalized = np.array([
            [0.8, 0.2, 0],
            [0, 1, 0],
            [0.84, 0.1, 0.5],
            [0.33, 0.33, 0.33],
            [0.01, 0.221, 0.88],
            [0.12223, 0.7234, 0.6],
            [0.3, 0.9, 0.1],
            [1, 0, 0.2],
        ])
        Xi_row_norms = np.linalg.norm(Xi_unnormalized, axis=1, keepdims=True)
        Xi = Xi_unnormalized / Xi_row_norms

        # Inverse time parameter
        # beta == 1 -> TF expressions tend to the global average
        # beta == 10 -> TF expressions tending to some local averages
        # beta == 100 -> Stable attractors present in each enhancer
        beta = 1

        # Baseline activity vector
        w = np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])

        # Dynamics
        def enhancer_net(x):
            return np.matmul(Xi.transpose(), softmax(w + beta * np.matmul(Xi, x))) - x

        # Scale factor for zooming in
        SCALE_FACTOR_X = 2
        SCALE_FACTOR_Y = 2
        SCALE_FACTOR_Z = 3
        SCALE_FACTOR = [SCALE_FACTOR_X, SCALE_FACTOR_Y, SCALE_FACTOR_Z]

        # Systems to simulate close to each attractor
        POINTS_PER_ATTRACTOR = 10

        # Colors associated to each enhancer (row) including an additional color for average point
        COLORS = [BLUE, RED, ORANGE, GREEN, WHITE, PINK, TEAL, PURPLE] * POINTS_PER_ATTRACTOR

        # Generate some noisy initial positions close to each attractor
        initial_positions = []
        for _ in range(POINTS_PER_ATTRACTOR):
            for i in range(Xi.shape[0]):
                multiplicative_noise_factor = 1 + 0.5 * np.random.uniform(-1, 1)
                additive_noise_factor = np.random.uniform(-0.075, 0.075, Xi.shape[1])
                initial_positions += [SCALE_FACTOR * (multiplicative_noise_factor * Xi[i] + additive_noise_factor)]

        attractor_points = [Sphere(radius=0.065, color=COLORS[i]).move_to(SCALE_FACTOR * Xi[i]) for i in range(Xi.shape[0])]

        global_avg = np.mean(Xi.transpose(), axis=1)
        global_avg_point = Sphere(radius=0.065, color=GREY_C).move_to(SCALE_FACTOR * global_avg)

        self.add(global_avg_point, *attractor_points)

        # Color labels for identifying attractors
        color_labels = {
            BLUE: 'Blue',
            RED: 'Red',
            ORANGE: 'Orange',
            GREEN: 'Green',
            WHITE: 'White',
            PINK: 'Pink',
            TEAL: 'Teal',
            PURPLE: 'Purple',
            GREY_C: 'Grey'
        }

        # Printing some high cosine similarities between attractors
        print('Cosine similarities:')
        for i in range(Xi.shape[0]):
            for j in range(Xi.shape[0]):
                similarity = self.cosine_similarity(Xi[i], Xi[j])
                if i != j and similarity > 0.9:
                    print(f'Enhancers {i} ({color_labels[COLORS[i]]}), {j} ({color_labels[COLORS[j]]}): {similarity}')
        print('\n')

        # Create the dynamical systems
        systems = DynamicalSystemFamily(
            scene=self,
            initial_positions=initial_positions,
            # System functions (reparametrized for zoom)
            dx=lambda x,y,z: SCALE_FACTOR_X * enhancer_net(np.array([x, y, z])/ SCALE_FACTOR)[0],
            dy=lambda x,y,z: SCALE_FACTOR_Y * enhancer_net(np.array([x, y, z])/ SCALE_FACTOR)[1],
            dz=lambda x,y,z: SCALE_FACTOR_Z * enhancer_net(np.array([x, y, z])/ SCALE_FACTOR)[2],
            # Some style parameters
            speed_rate=0.5,
            point_radius=0.015,
            point_color=GREY,
            # fade_out_trace=True,
            # amount_to_not_fade_out_trace_before=1,
            # trace_fadeout_decrease_factor=0.2,
            # max_number_of_trace_lines=250,
            color=COLORS
        )

        # Set color to system traces
        for i, s in enumerate(systems.systems):
            s.set_color(Color(COLORS[i]))

        # Center camera on the attractors
        self.camera.frame.move_to(Xi.mean())
        systems.add_to_scene()

        # Showtime!
        self.wait(15)
