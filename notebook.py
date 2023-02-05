import sys
# Don't know why but ManimGL doesn't add current working directory as part of the PATH.
# Doing this so I can import dynamical_systems.
sys.path.append('/Users/matiaspalumbo/Documents/Manim stuff/ManimGL')

from manimlib import *
from dynamical_systems import *
import numpy as np
import math
import colour as col


x_function = lambda x,y: y
y_function = lambda x,y: - b * y - math.sin(x) + k

# Pendulum with (maybe) friction and (maybe) constant forcing
b = 0.5
k = 0.5
pendulum_x = lambda x,y: y
pendulum_y = lambda x,y: - b * y - math.sin(x) + k

factor = 10
pendulum_x_scaled = lambda x,y: y
pendulum_y_scaled = lambda x,y: - b * y - math.sin(x / factor) * factor + k


pendulum_x_3d = lambda x,y,z: y
pendulum_y_3d = lambda x,y,z: - b * y - math.sin(x) + k
pendulum_z_3d = lambda x,y,z: math.cos(z)


beta = 1
tau = 2
nu = 1
mu = 1
epidemic_x = lambda S,I: - beta * S * I + mu * (tau - S - I)
epidemic_y = lambda S,I: beta * S * I - nu * I


periodic_x = lambda x,y: math.cos(y)
periodic_y = lambda x,y: math.cos(x)


predator_x = lambda x,y: x * (1 - x) - x * y
predator_y = lambda x,y: y * (1 - y / x)



class DynamicalSystemsScene(Scene):
    def construct(self):
        plane = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plane)



        # points = [[-3, 3], [-4.5,0.5], [2,1.5], [6,-3], [-1,-2], [-3, -2], [-4, -1.5]]
        # point = points[0]

        points = [[i, 1] for i in range(-5, 5)]

        systems = DynamicalSystemFamily(
            scene=self,
            initial_positions=points,
            dx=pendulum_x,
            dy=pendulum_y,
            # show_snapshots=True,
            time_domain=[0,10],
            color_code_velocity=True,
        )
        print('hi')

        # color1 = col.Color('#3e99a0')
        # color2 = col.Color('#39c689')
        # colors = color1.range_to(color2, len(points))

        # color1 = col.Color('#265e62')
        # color2 = col.Color('#63e8ce')
        # colors = color1.range_to(color2, len(points))

        # for i, color in enumerate(colors):
        #     systems.systems[i].trace.stroke_color = color.hex

        # system = DynamicalSystem(
        #     scene=self,
        #     init_pos=point,
        #     dx=pendulum_x,
        #     dy=pendulum_y,
        # )


        systems.add_to_scene()

        # self.wait(120)

        # with updater: 1m 51s
        # with alwatys_redraw: much more



class PhasePlaneWithSolutionScene(Scene):
    def construct(self):
        plane = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plane)

        phase_plane = PhasePlane(self, plane, pendulum_x, pendulum_y, color=GREEN)
        phase_plane.add_to_scene()

        color1 = col.Color('#265e62')
        color2 = col.Color('#63e8ce')
        colors = color1.range_to(color2, len(phase_plane.systems))

        for i, color in enumerate(colors):
            phase_plane.systems[i].trace.stroke_color = color.hex


        # system = DynamicalSystem(scene=self, dx=x_function, dy=y_function, initial_pos = [2,-3])
        # system.add_to_scene()

        self.wait(4)



class SolutionThroughPointScene(Scene):
    def construct(self):
        plane = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plane)

        pos = [-2.3, 1]

        system = DynamicalSystem(scene=self, init_pos=pos, time_domain=[0,50], dx=pendulum_x, dy=pendulum_y, color=RED)
        system.add_to_scene()

        system2 = DynamicalSystem(scene=self, init_pos=pos, time_domain=[0,50], dx=periodic_x, dy=pendulum_y)
        system2.add_to_scene()

        system2 = DynamicalSystem(scene=self, init_pos=pos, time_domain=[0,50], dx=pendulum_y, dy=periodic_x)
        system2.add_to_scene()

        self.wait(5)



class PhasePlaneScene(Scene):
    def construct(self):
        plane = NumberPlane(background_line_style={'stroke_color':GREY, 'stroke_opacity':0.6})#, x_range=[0,6], y_range=[0,6])
        self.add(plane)

        phase_plane = PhasePlane(
            scene=self,
            plane=plane,
            dx=pendulum_x,
            dy=pendulum_y,
            # color=[BASE_STYLE.style['color'], '#7ac6cc'],
            color_code_velocity=True,
            # show_snapshots=True,
            # show_points=False,
            # point_radius=0.025,
            # width=2.5,
            # time_domain=[-10,10]
        )

        # solution = DynamicalSystemSnapshot(
        #     scene=self,
        #     init_pos=[-PI,.5],
        #     plane=plane,
        #     dx=pendulum_x,
        #     dy=pendulum_y,
        #     color=RED,
        #     time_domain=[0,6]
        #     # point_radius=0.025,
        #     # width=2.5,
        # )




        # cool strong red
        strong_red = col.Color('#ab5459')
        aqua = col.Color('#5ba486')
        color1 = col.Color('#265e62')
        color2 = col.Color('#63e8ce')
        # color2 = col.Color('#b5dfe2')
        # colors = color1.range_to(color2, len(phase_plane.systems))
        color2 = Color('#c9ff00')
        # colors = aqua.range_to(strong_red, len(phase_plane.systems))
        # colors = strong_red.range_to(color2, len(phase_plane.systems))

        # gradient = generate_color_gradient([Color('blue'), Color('red'), Color('white'), Color('green'), Color('yellow'), Color('blue')], int(135 / 5))
        # gradient = generate_color_gradient(
        #     # [Color('#217074'), Color('#37745B'), Color('#8B9D77'), Color('#E7EAEF'), Color('#EDC5AB'), Color('#EDC5AB')],
        #     [Color('#217074'), Color('#37745B'), Color('#8B9D77'), Color('#8B9D77'), Color('#37745B'), Color('#217074')],
        #     math.ceil(153 / 5)
        # )

        # print(len(phase_plane.systems))
        # length = 135
        # print(135/5)
        # print(len(gradient))
        # print(len(phase_plane.systems))

        # for i in range(len(phase_plane.systems)):
        #     phase_plane.systems[i].set_color(gradient[i])

        # for i in range(len(gradient)):
        #     phase_plane.systems[i].set_color(gradient[i])

        phase_plane.add_to_scene()
        # solution.add_to_scene()

        # self.wait(10)



class PhasePlane3DScene(ThreeDScene):
    def construct(self):
        sigma = 10
        beta = 8/3  
        rho = 28    
        alpha = 0.1

        OVER_FLOW_LIMIT = 100
        def prevent_overflow(n):
            return n if n < OVER_FLOW_LIMIT else 0

        lorentz_x = lambda x,y,z: prevent_overflow(sigma * (y - x))
        lorentz_y = lambda x,y,z: prevent_overflow(rho * x - y - x * z / alpha)
        lorentz_z = lambda x,y,z: prevent_overflow(x * y / alpha - beta * z)



        phi = 60
        theta = -30
        self.set_camera_orientation(phi=phi*DEGREES, theta=theta*DEGREES)

        axis_config = dict(tip_length=0.2, tip_width=0.2, fill_opacity=0.3)
        axes = ThreeDAxes(axis_config=axis_config, z_axis_config=axis_config)
        self.add(axes)

        self.begin_ambient_camera_rotation(rate=0.1)

        # self.begin_ambient_camera_rotation(rate=0.1)

        phase_plane = DynamicalSystem(
            scene=self,
            init_pos=[0,2,0],
            # plane=axes,
            dx=lorentz_x,
            dy=lorentz_y,
            dz=lorentz_z,
            speed_rate=0.05
        )
        phase_plane.add_to_scene()

        self.wait(30)




class BifurcationScene(Scene):
    # mu = DecimalNumber(-0.5)
    k = DecimalNumber(0.5)
    b = DecimalNumber(0.9)

    def construct(self):
        plane = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plane)

        pendulum_x = lambda x,y: y
        pendulum_y = lambda x,y: - self.b.get_value() * y - math.sin(x) + self.k.get_value()

        # hopf_x = lambda x,y: y - x**3 + self.mu.get_value() * x
        # hopf_y = lambda x,y: - x

        # MAX_VALUE = 10
        # lambda x,y: y - x**3 + self.mu.get_value() * x if y - x**3 + self.mu.get_value() * x < MAX_VALUE else MAX_VALUE,
        # lambda x,y: - x if - x < MAX_VALUE else MAX_VALUE,

        def get_phase_plane():
            phase_plane = PhasePlane(
            scene=self,
            plane=plane,
            dx=pendulum_x,
            dy=pendulum_y,
            show_snapshots=True,
            show_points=False,
            # point_radius=0.025,
            width=2,
            time_domain=[0,8]
        )
            return phase_plane

        def get_updated_phase_plane():
            system = get_phase_plane()
            mobjs = [s.forward_trace for s in system.systems]
            # self.add(*mobjs)
            return VGroup(*mobjs)


        # self.mu.add_updater(lambda n, dt: n.set_value(n.get_value() + 0.25*dt))
        self.b.add_updater(lambda n, dt: n.set_value(n.get_value() - 0.1*dt) if n.get_value() - 0.25*dt > 0 else n.set_value(0))
        
        # self.mu.add_updater(lambda n, dt: n.set_value(n.get_value() + 0.25*dt))# if n.get_value() - 0.25*dt > 0 else n.set_value(0))

        phase_plane = always_redraw(get_updated_phase_plane)
        # mobjs = [s.forward_trace for s in phase_plane.submobjects]
        # self.add(*mobjs)
        # self.add(phase_plane)
        # phase_plane.add_updater(lambda p: get_updated_phase_plane())

        numbers_group = VGroup(self.b).arrange(DOWN).to_corner(UR)

        self.add(phase_plane, numbers_group)
        self.wait(2)


        # system = DynamicalSystem(scene=self, dx=x_function, dy=y_function, initial_pos=[-1,1.7])

        # solution = system.get_solution_through_point(point=np.array([-0.4, -2, 0]), time_period=[-3,50])[0]
        # self.add(Dot(np.array([-.4, -2,0])))

        # self.add(solution)
        # self.wait(5)



class TestBifurcationScene(Scene):
    # mu = DecimalNumber(-0.5)
    k = DecimalNumber(0.5)
    b = DecimalNumber(0.1)

    def construct(self):
        plane = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plane)

        pendulum_x = lambda x,y: y
        pendulum_y = lambda x,y: - self.b.get_value() * y - math.sin(x) + self.k.get_value()

        phase_plane = Bifurcation(
            scene=self,
            plane=plane,
            dx=pendulum_x,
            dy=pendulum_y,
            parameter=self.b,
            time_domain=[0,8]
        )

        phase_plane.add_to_scene()
        numbers_group = VGroup(self.b).arrange(DOWN).to_corner(UR)

        self.add(numbers_group)
        self.wait(.5)

        # numbers_group = VGroup(self.b).arrange(DOWN).to_corner(UR)

        # self.add(phase_plane, numbers_group)
        # self.wait(2)


        # system = DynamicalSystem(scene=self, dx=x_function, dy=y_function, initial_pos=[-1,1.7])

        # solution = system.get_solution_through_point(point=np.array([-0.4, -2, 0]), time_period=[-3,50])[0]
        # self.add(Dot(np.array([-.4, -2,0])))

        # self.add(solution)
        # self.wait(5)






class TestScene(Scene):
    def construct(self):
        plane = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plane)

        system = DynamicalSystemSnapshot(
            scene=self,
            init_pos=[1,0],
            dx=periodic_x,
            dy=periodic_y,
            time_domain=[-10,10]
        )
        print(type(self))
        system.add_to_scene()
        # self.wait()
        # self.add(system)

        # self.wait(3)
        # system.pause_update()
        # self.play(system.shift, 3*UP)
        # system.resume_update()