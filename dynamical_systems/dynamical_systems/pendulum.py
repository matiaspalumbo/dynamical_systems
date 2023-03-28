from manimlib import *
from dynamical_systems import *
from colour import Color


class Pendulum:
    def __init__(
            self,
            scene,
            initial_angle=0,
            center=UP,
            scale_factor=2,
            speed_rate=1,
            color=BLUE,
            point_radius=0.06,
            friction_factor=0
        ):
        self.friction_factor = friction_factor

        g = 9.81
        d1theta = lambda x,y: y
        d2theta = lambda x,y: - self.friction_factor * y - g * math.sin(x)

        self.scene = scene

        self.scale_factor = scale_factor
        self.speed_rate = speed_rate

        self.center = copy.deepcopy(center)
        self.center_point = Dot(
            center, radius=0.06, color='#343434'
        )
        self.color = color
        self.point_radius = point_radius
        self.coords = [
            initial_angle,
            d2theta(0, initial_angle)
        ]

        self.point1 = Dot(
            self.get_sincos_point(self.coords[0]),
            radius=point_radius
        )
        self.rod1 = Line(
            ORIGIN,
            self.get_sincos_point(self.coords[0]),
            color=self.color,
        )

        def get_point(p, dt):
            self.coords[0] = self.coords[0] + d1theta(*self.coords) * dt * self.speed_rate
            self.coords[1] = self.coords[1] + d2theta(*self.coords) * dt * self.speed_rate

            self.rod1.set_points_by_ends(
                self.center + ORIGIN,
                self.center + self.get_sincos_point(self.coords[0]),
            )
            self.point1.move_to(
                self.center + self.get_sincos_point(self.coords[0]),
            )

        def get_rod1():
            return self.rod1
        
        self.rod1too = always_redraw(get_rod1)
        self.point1.add_updater(get_point)

    def get_sincos_point(self, t):
        return self.scale_factor * np.array([np.sin(t), -np.cos(t), 0])
    
    def add_to_scene(self):
        self.scene.add(self.rod1too, self.point1)

    def add_center_point(self):
        self.scene.add(Dot(self.center, radius=0.06, color='#343434'))


class DoublePendulum:
    def __init__(
            self,
            scene,
            initial_angle1=0,
            initial_angle2=0,
            center=UP,
            scale_factor=2,
            speed_rate=1,
            color=BLUE,
            point_radius=0.06,
        ):
        L1, L2 = 1, 1
        m1, m2 = 1, 1
        g = 9.81
        d1theta1 = lambda t1, z1, t2, z2: z1
        d2theta1 = lambda t1, z1, t2, z2: (m2*g*np.sin(t2)*np.cos(t1-t2) - m2*np.sin(t1-t2)*(L1*z1**2*np.cos(t1-t2) + L2*z2**2) - (m1+m2)*g*np.sin(t1)) / L1 / (m1 + m2*np.sin(t1-t2)**2)
        d1theta2 = lambda t1, z1, t2, z2: z2
        d2theta2 = lambda t1, z1, t2, z2: ((m1+m2)*(L1*z1**2*np.sin(t1-t2) - g*np.sin(t2) + g*np.sin(t1)*np.cos(t1-t2)) + m2*L2*z2**2*np.sin(t1-t2)*np.cos(t1-t2)) / L2 / (m1 + m2*np.sin(t1-t2)**2)

        self.scene = scene

        self.scale_factor = scale_factor
        self.speed_rate = speed_rate

        self.center = copy.deepcopy(center)
        self.center_point = Dot(
            center, radius=0.06, color='#343434'
        )
        self.color = color
        self.point_radius = point_radius
        self.coords = [
            initial_angle1,
            d2theta1(initial_angle1, 0, initial_angle2, 0),
            initial_angle2,
            d2theta2(initial_angle1, 0, initial_angle2, 0),
        ]

        self.point1 = Dot(
            self.get_sincos_point(self.coords[0]),
            radius=point_radius
        )
        self.rod1 = Line(
            ORIGIN,
            self.get_sincos_point(self.coords[0]),
            color=self.color,
        )
        self.point2 = Dot(
            self.get_sincos_point(self.coords[0]) + self.get_sincos_point(self.coords[2]),
            radius=point_radius
        )        
        self.rod2 = Line(
            self.get_sincos_point(self.coords[0]),
            self.get_sincos_point(self.coords[0]) + self.get_sincos_point(self.coords[2]),
            color=self.color
        )
        self.pendulum_points = VGroup(self.point2, self.point1)

        def get_pendulum_points(p, dt):
            self.coords[0] = self.coords[0] + d1theta1(*self.coords) * dt * self.speed_rate
            self.coords[1] = self.coords[1] + d2theta1(*self.coords) * dt * self.speed_rate
            self.coords[2] = self.coords[2] + d1theta2(*self.coords) * dt * self.speed_rate
            self.coords[3] = self.coords[3] + d2theta2(*self.coords) * dt * self.speed_rate

            self.rod1.set_points_by_ends(
                self.center + ORIGIN,
                self.center + self.get_sincos_point(self.coords[0]),
            )
            self.rod2.set_points_by_ends(
                self.center + self.get_sincos_point(self.coords[0]),
                self.center + self.get_sincos_point(self.coords[0]) + self.get_sincos_point(self.coords[2]),
            )
            self.pendulum_points.submobjects[0].move_to(
                self.center + self.get_sincos_point(self.coords[0]) + self.get_sincos_point(self.coords[2]),
            )
            self.pendulum_points.submobjects[1].move_to(
                self.center + self.get_sincos_point(self.coords[0]),
            )
        def get_rod2():
            return self.rod2
        def get_rod1():
            return self.rod1
        
        self.rod2too = always_redraw(get_rod2)
        self.rod1too = always_redraw(get_rod1)
        self.pendulum_points.add_updater(get_pendulum_points)
        
    def get_sincos_point(self, t):
        return self.scale_factor * np.array([np.sin(t), -np.cos(t), 0])

    def add_to_scene(self):
        self.scene.add(self.rod1too, self.rod2too, self.pendulum_points)

    def add_center_point(self):
        self.scene.add(Dot(self.center, radius=0.06, color='#343434'))
