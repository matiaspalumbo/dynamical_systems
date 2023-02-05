import sys
# Don't know why but ManimGL doesn't add current working directory as part of the PATH.
# Doing this so I can import dynamical_systems.
sys.path.append('/Users/matiaspalumbo/Documents/Manim stuff/ManimGL')

from manimlib import *
from dynamical_systems_NEW_POINT_AND_TRACE import *
import numpy as np
import math
from colour import Color

class EscenaAtractorDeLorentzVideo(ThreeDScene):
    def begin_ambient_camera_rotation(self, rate=0.003):
        self.camera.frame.add_updater(lambda camFrame: camFrame.rotate(angle=rate))

    def construct(self):
        # Definimos el sistema de Lorentz
        sigma = 10
        beta = 8/3  
        rho = 28    
        alpha = 0.12 # escala el sistema
        lorentz_x = lambda x,y,z: sigma * (y - x)
        lorentz_y = lambda x,y,z: rho * x - y - x * z / alpha
        lorentz_z = lambda x,y,z: x * y / alpha - beta * z

        # Agregamos ejes a la escena
        ejes_config = dict(tip_length=0.2, tip_width=0.2, fill_opacity=0.3)
        ejes = ThreeDAxes(
            x_range=[-20, 20],
            y_range=[-20, 20],
            z_range=[-20, 20],
            axis_config=ejes_config,
            z_axis_config=ejes_config
        )
        self.add(ejes)

        # Pos. inicial del sistema
        posicion_inicial = [0, 2, 0]

        # Movemos la cámara para tener un ángulo mejor
        r1 = Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.camera.frame.set_orientation(rot)
        self.camera.frame.shift(3*OUT)

        # Configuramos que la cámara gire lentamente a medida que se traza el sistema
        self.begin_ambient_camera_rotation(rate=0.003)

        # Creamos el sistema
        sistema = DynamicalSystem(
            scene=self,
            dx=lorentz_x,
            dy=lorentz_y,
            dz=lorentz_z,
            init_pos=posicion_inicial,
            color_code_velocity="from_trace",
            fade_out_trace=True,
            speed_rate=.2,
            width=2.5,
            point_radius=0.035
        )

        # Para que este sistema se coloree bien, conviene cambiar la constante COLOR_CODING_SCALE_FACTOR
        # a algo mayor. Para el video que está en el drive, la cambié a 3
        sistema.add_to_scene()
        self.wait(120)
        # self.play(FadeOut(sistema.trace), run_time=3)


class EscenaSistemaDinamicoFadeOut(Scene):
    """Escena con un sistema dinámico que se actualiza en cada frame.

    Cuando se crea el sistema dinámico, se pueden pasar bastantes parámetros que modifican su estilo.
    Se pueden encontrar todos estos parámetros en la constante BASE_STYLE.
    
    El parámetro show_point permite mostrar o no el punto del sistema. Por defecto es True.
    Si es False, solo se grafica la traza del sistema.

    El parámetro color_code_velocity colorea el sistema
    de acuerdo a su velocidad. Puede ser igual a "from_trace" (calcula la velocidad asociada a cada color
    mediante una simulación del sistema antes de crearlo) o "from_plane" (hace el mismo cálculo pero
    aplicando el sistema a los pares de enteros del plano). color_code_velocity es False por defecto.
    El parámetro de estilo velocity_colors permite personalizar los tres colores básicos en los que se divide
    el coloreo según valocidad. Por defecto, son verde, amarillo y rojo
    """
    
    def construct(self):
        # Agreamos un plano a la escena
        plano = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plano)

        # Definimos el sistema, en este caso un péndulo con fricción y fuerza constante
        b = 0.5
        k = 0.5
        pendulo_x = lambda x,y: y
        pendulo_y = lambda x,y: - b * y - math.sin(x) + k

        f_x = lambda x,y: math.cos(y)
        f_y = lambda x,y: math.cos(x)

        # Posición inicial
        posicion_inicial = [0, 2]

        # Creamos el sistéma dinámico
        sistema = DynamicalSystem(
            scene=self,
            dx=pendulo_x,
            dy=pendulo_y,
            init_pos=posicion_inicial,
            # color_code_velocity="from_trace",
            fade_out_trace=True,
            width=2.5,
            point_radius=0.035
        )

        sistema.add_to_scene()
        self.wait(10)


class HalvorsenAttractorScene(ThreeDScene):
    def begin_ambient_camera_rotation(self, rate=0.003):
        def get_dt(dt, offset=0):
            return 0.1 + math.cos(dt + offset)

        about_point = np.array([-0.67922174, -0.67611461, -0.67617357])
        self.camera.frame.move_to(about_point)
        self.camera.frame.add_updater(
            lambda camFrame, dt: camFrame.rotate(
                angle=rate*2.5,
                # axis=get_dt(dt)*OUT + get_dt(dt, PI/2)*UP + get_dt(dt, PI)*RIGHT,
                axis=get_dt(dt)*OUT,
                about_point=about_point,
            )
        )

    def construct(self):

        a = 1.89
        alpha = .5 # escala el sistema
        halvorsen_x = lambda x,y,z: - a * x - 4 * y - 4 * z - (y/alpha)**2
        halvorsen_y = lambda x,y,z: - a * y - 4 * z - 4 * x - (z/alpha)**2
        halvorsen_z = lambda x,y,z: - a * z - 4 * x - 4 * y - (x/alpha)**2


        # sigma = 10
        # beta = 8/3  
        # rho = 28    
        # alpha = 0.15 # escala el sistema
        # lorentz_x = lambda x,y,z: sigma * (y - x)
        # lorentz_y = lambda x,y,z: rho * x - y - x * z / alpha
        # lorentz_z = lambda x,y,z: x * y / alpha - beta * z

        # Don't want axes for now
        # axes_config = dict(tip_length=0.2, tip_width=0.2, fill_opacity=0.3)
        # axes_length = 50
        # axes = ThreeDAxes(
        #     x_range=[-axes_length, axes_length],
        #     y_range=[-axes_length, axes_length],
        #     z_range=[-axes_length, axes_length],
        #     axis_config=axes_config,
        #     z_axis_config=axes_config
        # )
        # self.add(axes)

        # Pos. inicial del sistema
        # initial_position = [-1.48*alpha, -1.51*alpha, 2.04*alpha]
        # initial_position = [-0.67922174, -0.67611461, -0.67617357] # Average point

        # Movemos la cámara para tener un ángulo mejor
        r1 = Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.camera.frame.set_orientation(rot)
        # self.camera.frame.shift(3*OUT)

        # Configuramos que la cámara gire lentamente a medida que se traza el sistema
        self.begin_ambient_camera_rotation(rate=0.003)

        bd = 1.25
        step = 0.4 # .25
        initial_positions = set([
            (x, y, z) for x in np.arange(-bd, bd - 0.1, step)
            for y in np.arange(-bd, bd - 0.1, step)
            for z in np.arange(-bd, bd -0.1, step)
        ]) - {(0,0,0)}
        # initial_positions = list(initial_positions)[:1]

        # posiciones_iniciales = set([(x*alpha, 0, 0) for x in np.arange(-3, 3, 0.1)] + [(0, y*alpha, 0) for y in np.arange(-3, 2.9, 0.1)] + [(0, 0, z*alpha) for z in np.arange(-3, 3, 0.1)]) - {(0, 0, 0)}
        # print(posiciones_iniciales)
        # posiciones_iniciales = [(0, 1, 0)]
        # sistema = DynamicalSystemFamily(
        
        some_velocity_colors = [
            ['#8ecae6', '#219ebc', '#045a85'], # blues
            ['#cad2c5', '#84a98c', '#52796f'], # greens - alternative last: '#354f52'
            ['#ffcdb2', '#ffb4a2', '#e5989b'], # oranges/salmon
            ['#a3c9a8', '#69a297', '#50808e'], # teals?
            ['#dca2ad', '#ce7d8d', '#b9465c'], # purple ish
        ]

        color_index = 4

        sistema = DynamicalSystemFamily(
            scene=self,
            # init_pos=init_pos,
            initial_positions=initial_positions,
            dx=halvorsen_x,
            dy=halvorsen_y,
            dz=halvorsen_z,
            color_code_velocity="manual",
            fade_out_trace=True,
            point_radius=0.015, # parámetro de estilo; es el radio del punto del sistema
            point_color=GREY_B,
            width=2.5,
            speed_rate=0.5,
            # velocity_colors= [(GREEN, 0), (YELLOW, 10), (RED, 20)], # The first and second number don't do anything for now
            velocity_colors=[(some_velocity_colors[color_index][0], 0), (some_velocity_colors[color_index][1], 2), (some_velocity_colors[color_index][2], 15)], # The first and second number don't do anything for now
            trace_fadeout_decrease_factor=0.085, # 0.2
            amount_to_not_fade_out_trace_before=0.15,
            line_trace_overlap_buff=0.0225,
            precision_multiplier_if_trace_too_rough=2,
        )

        # Para que este sistema se coloree bien, conviene cambiar la constante COLOR_CODING_SCALE_FACTOR
        # a algo mayor. Para el video que está en el drive, la cambié a 3 [edit: ???]
        # self.camera.frame.shift(3*OUT)
        sistema.add_to_scene()
        self.wait(600)
        # self.play(FadeOut(sistema.trace), run_time=3)

# with improvement: 68.66s user 4.66s system 126% cpu 57.772 total
# wout improvement: 74.60s user 4.64s system 124% cpu 1:03.76 total




class MultipleLorentzAttractorScene(ThreeDScene):
    def begin_ambient_camera_rotation(self, rate=0.003):
        def get_dt(dt, offset=0):
            return 0.1 + math.cos(dt + offset)

        about_point = np.array([0, 0, 3.5])
        self.camera.frame.move_to(about_point)
        self.camera.frame.add_updater(
            lambda camFrame, dt: camFrame.rotate(
                angle=rate*3.25,
                axis=get_dt(dt)*OUT + get_dt(dt, PI/2)*UP + get_dt(dt, PI)*RIGHT,
                # axis=get_dt(dt)*OUT,
                about_point=about_point,
            )
        )

    def construct(self):
        sigma = 10
        beta = 8/3  
        rho = 28    
        alpha = 0.125 # escala el sistema
        lorentz_x = lambda x,y,z: sigma * (y - x)
        lorentz_y = lambda x,y,z: rho * x - y - x * z / alpha
        lorentz_z = lambda x,y,z: x * y / alpha - beta * z


        r1 = Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.camera.frame.set_orientation(rot)

        # Configuramos que la cámara gire lentamente a medida que se traza el sistema
        self.begin_ambient_camera_rotation(rate=0.003)

        bd = 2
        step = .5 # .25
        initial_positions = set([
            (x, y, z) for x in np.arange(0, bd, step)
            for y in np.arange(-bd/2, bd/2, step)
            for z in np.arange(0, bd, step)
        ])
        initial_positions -= set([pos for pos in initial_positions if pos[0] == 0 and pos[1] == 0])
        # initial_positions = list(initial_positions)[4:5]

        some_velocity_colors = [
            ['#8ecae6', '#219ebc', '#045a85'], # blues
            ['#cad2c5', '#84a98c', '#52796f'], # greens - alternative last: '#354f52'
            ['#ffcdb2', '#ffb4a2', '#e5989b'], # oranges/salmon
            # ['#a3c9a8', '#69a297', '#50808e'], # teals?
            ['#bdc7b7', '#69a297', '#487481'], # teals?
            ['#dca2ad', '#ce7d8d', '#b9465c'], # purple ish
        ]

        color_index = 3

        style_for_long_trace = dict(
            trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
            amount_to_not_fade_out_trace_before=7.5,
            line_trace_overlap_buff=0.0225,
            precision_multiplier_if_trace_too_rough=3,
        )

        style_for_short_trace = dict(
            trace_fadeout_decrease_factor=0.1, #0.05, #.025, # 0.3
            amount_to_not_fade_out_trace_before=0.25, #500, #1.25, #7.5,
            line_trace_overlap_buff=0.0225,
            precision_multiplier_if_trace_too_rough=3,
        )

        sistema = DynamicalSystemFamily(
            scene=self,
            initial_positions=initial_positions,
            dx=lorentz_x,
            dy=lorentz_y,
            dz=lorentz_z,
            color_code_velocity="manual",
            fade_out_trace=True,
            point_radius=0.015, # parámetro de estilo; es el radio del punto del sistema
            point_color=GREY_B,
            width=2.5, #2.3
            speed_rate=0.325,
            # velocity_colors= [(GREEN, 0), (YELLOW, 10), (RED, 20)], # The first and second number don't do anything for now
            velocity_colors=[
                (some_velocity_colors[color_index][0], 0),
                (some_velocity_colors[color_index][1], 7.5),
                (some_velocity_colors[color_index][2], 20)
            ], # The first and second number don't do anything for now
            **style_for_long_trace
        )

        # sistema_test = DynamicalSystem(
        #     scene=self,
        #     init_pos=(.5, 0, .5),
        #     dx=lorentz_x,
        #     dy=lorentz_y,
        #     dz=lorentz_z,
        #     color_code_velocity="manual",
        #     fade_out_trace=False,
        #     point_radius=0.025, # parámetro de estilo; es el radio del punto del sistema
        #     width=2.5,
        #     speed_rate=0.325,
        #     # velocity_colors= [(GREEN, 0), (YELLOW, 10), (RED, 20)], # The first and second number don't do anything for now
        #     velocity_colors=[
        #         (some_velocity_colors[color_index][0], 0),
        #         (some_velocity_colors[color_index][1], 7.5),
        #         (some_velocity_colors[color_index][2], 20)
        #     ], # The first and second number don't do anything for now
        #     # trace_fadeout_decrease_factor=0.025, # 0.3
        #     # amount_to_not_fade_out_trace_before=0, #7.5,
        #     line_trace_overlap_buff=0.0225,
        #     precision_multiplier_if_trace_too_rough=15,
        # )

        # Para que este sistema se coloree bien, conviene cambiar la constante COLOR_CODING_SCALE_FACTOR
        # a algo mayor. Para el video que está en el drive, la cambié a 3 [edit: ???]
        sistema.add_to_scene()
        self.wait(5)
        # self.wait(20)
        # self.wait(60)
        # self.wait(30)
        # self.wait(120)

        # 1:21.08 total with improvement
        # 1:23.13 without improvement


        # 20s hd:
        #  7:16.27 total without improvement
        #  3:32.98 total with improvement YAY 

        # HD 60s 21:43.78 with improvement