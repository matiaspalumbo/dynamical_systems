import sys
# Don't know why but ManimGL doesn't add current working directory as part of the PATH.
# Doing this so I can import dynamical_systems.
sys.path.append('/Users/matiaspalumbo/dynamical_systems/dynamical_systems')

from manimlib import *
from dynamical_systems import *
import numpy as np
import math
from colour import Color


x_function = lambda x,y: y
y_function = lambda x,y: - b * y - math.sin(x) + k

# Pendulum with (maybe) friction and (maybe) constant forcing
b = 0.5
k = 0.5
pendulo_x = lambda x,y: y
pendulo_y = lambda x,y: - b * y - math.sin(x) + k

factor = 10
pendulo_x_scaled = lambda x,y: y
pendulo_y_scaled = lambda x,y: - b * y - math.sin(x / factor) * factor + k


pendulo_x_3d = lambda x,y,z: y
pendulo_y_3d = lambda x,y,z: - b * y - math.sin(x) + k
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


class EscenaSistemaDinamico(Scene):
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

        # Posición inicial
        posicion_inicial = [-1, 1.5]

        # Creamos el sistéma dinámico
        sistema = DynamicalSystem(
            scene=self,
            init_pos=posicion_inicial,
            dx=pendulo_x,
            dy=pendulo_y,
            color=ORANGE,
            color_code_velocity=False, # puede ser False, "from_trace" o "from_plane"
        )

        # Agregamos el sistema dinámico a la escena
        sistema.add_to_scene()

        self.wait(20)


class EscenaSistemaDinamicoBilateral(Scene):
    """Escena con un sistema dinámico que se mueve en ambas direcciones."""

    def construct(self):
        # Agreamos un plano a la escena
        plano = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plano)

        # Definimos el sistema, en este caso un péndulo con fricción y fuerza constante
        b = 0.5
        k = 0.5
        pendulo_x = lambda x,y: y
        pendulo_y = lambda x,y: - b * y - math.sin(x) + k

        # Posición inicial
        posicion_inicial = [0.2, 0.15]

        # Creamos el sistéma dinámico
        sistema = BilateralDynamicalSystem(
            scene=self,
            init_pos=posicion_inicial,
            dx=pendulo_x,
            dy=pendulo_y,
            color_code_velocity="from_plane", # coloreamos el sistema de acuerdo a la velocidad en cada punto
            fade_out_trace=True
        )

        # Agregamos el sistema dinámico a la escena
        sistema.add_to_scene()

        self.wait(15)


class EscenaSistemaDinamicoEstatico(Scene):
    """Escena con un sistema dinámico estático, correspondiente al
    dominio temporal especificado."""

    def construct(self):
        # Agreamos un plano a la escena
        plano = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plano)

        # Definimos un sistema, en este caso un péndulo con fricción y fuerza constante
        b = 0.5
        k = 0.5
        pendulo_x = lambda x,y: y
        pendulo_y = lambda x,y: - b * y - math.sin(x) + k

        # Posición inicial
        posicion_inicial = [0, 2.05]

        # Creamos el 'snapshot' del sistéma dinámico
        sistema = DynamicalSystemSnapshot(
            scene=self,
            init_pos=posicion_inicial,
            dx=pendulo_x,
            dy=pendulo_y,
            time_domain=[-7, 15], # t-dominio del sistema
            color_code_velocity="from_plane",
            velocity_colors=["#efccd4", "#dd94a5", "#cb5d77"]
        )

        sistema.add_to_scene()


        # Definamos otro sistem
        periodic_x = lambda x,y: math.cos(y)
        periodic_y = lambda x,y: math.cos(x)

        # Posición inicial
        posicion_inicial2 = [-3, -1]

        # Creamos el 'snapshot' del sistéma dinámico
        sistema2 = DynamicalSystemSnapshot(
            scene=self,
            init_pos=posicion_inicial2,
            dx=periodic_x,
            dy=periodic_y,
            time_domain=[0, 8.5], # t-dominio del sistema
            color=PURPLE
        )

        sistema2.add_to_scene()



class EscenaMuchosSistemasDinamicos(Scene):
    """Escena con una familia de sistemas dinámicos.
    
    La clase DynamicalSystemFamily permite crear rápidamente muchos sistemas dinámicos.

    El parámetro show_snapshots sirve para decirle al programa que cree sistemas que se actualizan
    en cada frame (show_snapshots=False) o snapshots de sistemas en un dominio de tiempo dado
    (show_snapshots=True). Por defecto, show_snapshos=False.

    También se puede pasar el parámetro show_points (True o False) para mostrar (o no) los
    puntos de cada sistema.

    En esta clase, el parámetro color puede ser un solo color, o una lista de colores
    cuya longitud no tiene que ser necesariamente igual a la cantidad de sistemas. En caso de no serlo,
    se genera colores intermedios para que el coloreo quede bien.

    También se pueden pasar parámetros para los sitemas individuales a graficar, como
    por ejemplo color_code_velocity.
    """

    def construct(self):
        # Agreamos un plano a la escena
        plano = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plano)

        # Definimos un sistema, en este caso un péndulo con fricción y fuerza constante
        b = 0.75
        k = 0.5
        pendulo_x = lambda x,y: y
        pendulo_y = lambda x,y: - b * y - math.sin(x) + k

        # Posiciones iniciales de los sistemas a graficar
        # En este caso son [-1,0], [-2,0], ..., [-5,0], [-1,-4] [-1,-3], ..., [-1, 4]
        posiciones_iniciales = [[-x, 0] for x in range(1, 6)] + [[-1, y] for y in range(-4, 5)]


        # Creamos todos los sistemas
        sistemas = DynamicalSystemFamily(
            scene=self,
            initial_positions=posiciones_iniciales,
            dx=pendulo_x,
            dy=pendulo_y,
            show_snapshots=False,
            point_radius=0.04 # parámetro de estilo; es el radio del punto del sistema
        )

        sistemas.add_to_scene()

        self.wait(10)


class EscenaPlanoDeFaseSnapshot(Scene):
    """Escena con el plano de fase de un sistema.
    
    La clase PhasePlane crea el plano de fase del sistema dado. Toma todos los pares de enteros
    del plano y genera sistemas con posición inicial en cada uno de esos puntos.

    Esta clase puede tomar los mismos parámetros que DynamicalSystemFamily, como por ejemplo
    show_snapshots y show_points.

    La clase PhasePlane necesita que le pasemos el plano sobre el cual trabajamos
    para que pueda calcular las posiciones iniciales de los sistemas.
    """

    def construct(self):
        # Agreamos un plano a la escena
        plano = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plano)

        # Definimos un sistema, en este caso un péndulo con fricción y fuerza constante
        periodic_x = lambda x,y: math.cos(y)
        periodic_y = lambda x,y: math.cos(x)

        # Creamos el plano de fase
        plano_de_fase = PhasePlane(
            scene=self,
            plane=plano,
            dx=periodic_x,
            dy=periodic_y,
            show_snapshots=True,
            show_points=False,
            time_domain=[0, 15],
            style=PHASE_PLANE_STYLE,
            color_code_velocity="from_plane"
        )

        plano_de_fase.add_to_scene()


class EscenaPlanoDeFaseVideo(Scene):
    """Escena con el plano de fase de un sistema."""

    def construct(self):
        # Agreamos un plano a la escena
        plano = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plano)

        # Definimos un sistema, en este caso un péndulo con fricción y fuerza constante
        periodic_x = lambda x,y: math.cos(y)
        periodic_y = lambda x,y: math.cos(x)

        # Creamos el plano de fase
        plano_de_fase = PhasePlane(
            scene=self,
            plane=plano,
            dx=periodic_x,
            dy=periodic_y,
            color=["#f8e9ec", "#cb5d77"],
            show_snapshots=False,
            show_points=True,
            style=PHASE_PLANE_STYLE
        )

        plano_de_fase.add_to_scene()

        self.wait(20)


class EscenaSeccionLocal(Scene):
    """Escena con un sistema dinámico y sus diferentes secciones locales."""

    def construct(self):
        # Agreamos un plano a la escena
        plano = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plano)

        # Definimos un sistema
        periodic_x = lambda x,y: math.cos(y)
        periodic_y = lambda x,y: math.cos(x)

        # Posiciones iniciales de los tres sistemas a graficar
        posiciones_iniciales = [[1, 0], [-3, 0], [-1, 1]]


        # Creamos todos los sistemas
        sistemas = DynamicalSystemFamily(
            scene=self,
            initial_positions=posiciones_iniciales,
            dx=periodic_x,
            dy=periodic_y,
            color=[PURPLE, BLUE, GREEN],
            local_section_perp_vector_color=WHITE
        )

        sistemas.add_to_scene()

        self.wait(1)

        for sistema in sistemas.systems:
            sistema.add_local_section()

        self.wait(10)


class EscenaCajaDeFlujo(Scene):
    """Escena con un sistema dinámico y sus diferentes secciones locales."""

    def construct(self):
        # Agreamos un plano a la escena
        plano = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plano)

        # Definimos un sistema
        periodic_x = lambda x,y: math.cos(y)
        periodic_y = lambda x,y: math.cos(x)

        # Posiciones iniciales de los tres sistemas a graficar
        posiciones_iniciales = [[1, 0], [-3, 0], [-1, 1]]


        # Creamos todos los sistemas
        sistemas = DynamicalSystemFamily(
            scene=self,
            initial_positions=posiciones_iniciales,
            dx=periodic_x,
            dy=periodic_y,
            color=[PURPLE, BLUE, GREEN],
            local_section_perp_vector_color=WHITE
        )

        sistemas.add_to_scene()

        self.wait(1)

        for sistema in sistemas.systems:
            # El parámetro is_flow_bow determina si se grafica
            # una sección local (False) o una caja de flujo (True)
            sistema.add_local_section(is_flow_box=True)

        self.wait(10)


class EscenaBifurcacion1(Scene):
    """Grafica un plano de fase de un sistema donde un parámetro se actualiza
    en cada frame."""

    def construct(self):
        plane = NumberPlane(background_line_style={'stroke_color':GREY})
        self.add(plane)

        # En este caso graficamos un péndulo con fricción y fuerza constante
        k = DecimalNumber(0.75)
        b = DecimalNumber(0.5)
        pendulo_x = lambda x,y: y
        pendulo_y = lambda x,y: - b.get_value() * y - math.sin(x) + k.get_value()

        plano_de_fase = Bifurcation(
            scene=self,
            plane=plane,
            dx=pendulo_x,
            dy=pendulo_y,
            parameter=k, # en este caso hacemos la bifurcación con respecto al parámetro k
            time_domain=[0,15],
            color_code_velocity=False,
            style=PHASE_PLANE_STYLE
        )

        k_texto = k.to_corner(UR)

        plano_de_fase.add_to_scene()
        self.add(k_texto)
        
        self.wait(8)


class EscenaBifurcacion2(Scene):
    """Grafica un plano de fase de un sistema donde un parámetro se actualiza
    en cada frame."""

    def construct(self):
        plane = NumberPlane(x_range=[-3,3], y_range=[-3,3],background_line_style={'stroke_color':GREY})
        self.add(plane)

        # En este caso graficamos un sistema donde hay bifurcación de Hopf
        mu = DecimalNumber(-0.5)
        hopf_x = lambda x,y: y - x**3 + mu.get_value() * x
        hopf_y = lambda x,y: - x

        plano_de_fase = Bifurcation(
            scene=self,
            plane=plane,
            dx=hopf_x,
            dy=hopf_y,
            parameter=mu,
            time_domain=[0,15],
            color_code_velocity=False
        )

        mu_texto = mu.to_corner(UR)

        plano_de_fase.add_to_scene()
        self.add(mu_texto)
        
        self.wait(10)


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
            speed_rate=.2,
            width=2.5,
            point_radius=0.035
        )

        # Para que este sistema se coloree bien, conviene cambiar la constante COLOR_CODING_SCALE_FACTOR
        # a algo mayor. Para el video que está en el drive, la cambié a 3
        sistema.add_to_scene()
        self.wait(100)


class EscenaAtractorDeLorentzSnapshot(ThreeDScene):
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
        sistema = DynamicalSystemSnapshot(
            scene=self,
            dx=lorentz_x,
            dy=lorentz_y,
            dz=lorentz_z,
            init_pos=posicion_inicial,
            time_domain=[0,10],
            show_point=False,
            color_code_velocity="from_trace",
            speed_rate=.2,
            width=2.5,
            point_radius=0.035,
        )
        sistema.add_to_scene()
        self.wait(2)


class EscenaAtractorDeRosslerSnapshot(ThreeDScene):
    def begin_ambient_camera_rotation(self, rate=0.003):
        self.camera.frame.add_updater(lambda camFrame: camFrame.rotate(angle=rate))

    def construct(self):
        # Definimos el sistema de Rossler
        a = 1/4
        b = 1
        c = 5.5
        alpha2 = 0.5
        rossler_x = lambda x,y,z: - y - z
        rossler_y = lambda x,y,z: x + a * y
        rossler_z = lambda x,y,z: b * alpha2 + z * (x / alpha2 - c)

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
        posicion_inicial = [0, -2, 0]

        # Movemos la cámara para tener un ángulo mejor
        r1 = Rotation.from_rotvec(np.pi/4 * np.array([1, 0, 0]))
        r2 = Rotation.from_rotvec(np.pi/4 * np.array([0, 0, 1]))
        rot = r2 * r1
        self.camera.frame.set_orientation(rot)

        # Configuramos que la cámara gire lentamente a medida que se traza el sistema
        self.begin_ambient_camera_rotation(rate=0.003)

        # Creamos el sistema
        sistema = DynamicalSystemSnapshot(
            scene=self,
            dx=rossler_x,
            dy=rossler_y,
            dz=rossler_z,
            init_pos=posicion_inicial,
            time_domain=[0,200],
            show_point=False,
            color_code_velocity="from_trace",
            width=2.5,
            point_radius=0.035
        )

        # Para que este sistema se coloree bien, conviene cambiar la constante COLOR_CODING_SCALE_FACTOR
        # a algo mayor. Para el video que está en el drive, la cambié a 3
        sistema.add_to_scene()
        
        self.wait(30)
