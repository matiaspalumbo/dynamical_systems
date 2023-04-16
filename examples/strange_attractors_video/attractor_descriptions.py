import sys

# sys.path.append('/Users/matiaspalumbo/manim-custom')

from manimlib import *
from dynamical_systems import *
from sympy import Symbol, Expr, latex


class AttractorDescription(Scene):
    title = 'Attractor Name Here'
    functions = []
    parameters = dict()
    color = 'teal1'

    def _generate_system_latex(
        self,
        title: str,
        color: str,
        functions: List[Expr],
        parameters: dict[str, float] = None,
        params_box_buff: float=0.15,
        eval_functions=True,
        scale_title_by=1
    ):
        x = Symbol('x')
        y = Symbol('y')
        z = Symbol('z')
        alpha = Symbol('\\alpha')
        beta = Symbol('\\beta')
        gamma = Symbol('\\gamma')
        delta = Symbol('\\delta')
        varepsilon = Symbol('\\varepsilon')
        omega = Symbol('\\omega')
        rho = Symbol('\\rho')
        sigma = Symbol('\\sigma')
        zeta = Symbol('\\zeta')
        a = Symbol('a')
        b = Symbol('b')
        c = Symbol('c')
        d = Symbol('d')
        f = Symbol('f')
        non_tex_params = [symb.name for symb in [a, b, c, d, f]]

        # for i in range(3):
        #     print(eval(functions[i]))
        #     print(latex(eval(functions[i])))

        evaluated_functions = f"""
            \\left\\{{
            \\begin{{aligned}}
                x' &= {latex(eval(functions[0])) if eval_functions else functions[0]} \\\\
                y' &= {latex(eval(functions[1])) if eval_functions else functions[1]} \\\\
                z' &= {latex(eval(functions[2])) if eval_functions else functions[2]} \\\\
            \\end{{aligned}}\\right.
            """

        params = ""
        backslash = "\\"
        for name, value in parameters.items():
            params += f"{backslash+name if name not in non_tex_params else name} &= {value} \\\\"
        parameters_tex = f"""
            \\begin{{aligned}}
            {params}
            \\end{{aligned}}
        """
        title = Text(title).set_color_by_gradient(
            *SOME_VELOCITY_COLORS[color]
        ).scale(1.25*scale_title_by).to_corner(UL)
        system = Tex(
            evaluated_functions, color=GREY_A
        ).scale(0.75).to_corner(UL).next_to(
            title, direction=DOWN, aligned_edge=LEFT, buff=0.42
        )
        params = Tex(parameters_tex, color=GREY_C).scale(0.5).next_to(
            system, direction=DOWN, aligned_edge=LEFT, buff=0.225
            ).shift(0.3*RIGHT+0.35*DOWN)
        box = RoundedRectangle(
            corner_radius=0.25,
            height=params.get_height() + params_box_buff,
            width=params.get_width() + params_box_buff,
            fill_opacity=0,
            stroke_color=GREY_C,
            stroke_width=1.8
        ).surround(params, buff=0.4)
        return VGroup(title, system, params, box)
        
    def _display_text(self, text: VGroup):
        self.play(Write(text.submobjects[0]), run_time=3)
        self.wait()
        self.play(Write(text.submobjects[1]), run_time=5)
        self.play(Write(text.submobjects[2]), Write(text.submobjects[3]), run_time=1.5)
        self.wait(6.5)
        self.play(FadeOut(text), run_time=4)

    def generate_attractor_description(
            self,
            params_box_buff=0.15,
            eval_functions=True,
            scale_title_by=1,
        ):
        text = self._generate_system_latex(
            title=self.title,
            color=self.color,
            functions=self.functions,
            parameters=self.parameters,
            params_box_buff=params_box_buff,
            eval_functions=eval_functions,
            scale_title_by=scale_title_by,
        )
        self._display_text(text)


class LorentzAttractorDescription(AttractorDescription):
    title = 'The Lorenz Attractor'
    functions = [
        'sigma * (y - x)',
        'rho * x - y - x * z',
        'x * y - beta * z',
    ]
    parameters = dict(
        sigma = 10,
        beta = '8/3',
        rho = 28,
    )
    color = 'teal1'

    def construct(self):
        # text = self._generate_system_latex(title=self.title, color='teal1', functions=self.functions, parameters=self.parameters)
        # self.play(Write(text), run_time=5)
        # self.wait(.01)
        self.generate_attractor_description()


class HalvorsenAttractorDescription(AttractorDescription):
    title = 'The Halvorsen Attractor'
    functions = [
        '- alpha * x - 4 * y - 4 * z - (y)**2',
        '- alpha * y - 4 * z - 4 * x - (z)**2',
        '- alpha * z - 4 * x - 4 * y - (x)**2'
    ]
    parameters = dict(
        alpha = 1.89
    )
    color = 'magenta2'

    def construct(self):
        self.generate_attractor_description(params_box_buff=0.35)


class ChenLeeAttractorDescription(AttractorDescription):
    title = 'The Chen-Lee Attractor'
    functions = [ 
        'alpha * x - y * z',
        'beta * y + x * z',
        'delta * z + x * y / 3',
    ]
    parameters = dict(
        alpha = 5,
        beta = -10,
        delta = -0.38,
    )
    color = 'purple2'

    def construct(self):
        self.generate_attractor_description()


class AizawaAttractorDescription(AttractorDescription):
    title = 'The Aizawa Attractor'
    functions = [ 
        '(z - b) * x - delta * y',
        'delta * x + (z - b) * y',
        'c + a * z - z**3 / 3 - (x**2 + y**2) * (1 + varepsilon * z) + f * z * x**3'
    ]
    parameters = dict(
        a = 0.95,
        b = 0.7,
        c = 0.6,
        delta = 3.5,
        varepsilon = 0.25,
        f = 0.1
    )
    color = 'dark_purple'

    def construct(self):
        self.generate_attractor_description(params_box_buff=0.24)


class ThomasAttractorDescription(AttractorDescription):

    title = 'The Thomas Attractor'
    functions = [ 
'- \\omega x + \\sin(y)',
'- \\omega y + \\sin(z)',
'- \\omega z + \\sin(x)',
    ]
    parameters = dict(
        omega = 0.19
    )
    color = 'yellow_red_pastel'

    def construct(self):
        self.generate_attractor_description(eval_functions=False, params_box_buff=0.35)


class ChenCelikovskyAttractorDescription(AttractorDescription):

    title = 'The Chen-Celikovsky Attractor'
    functions = [ 
        'alpha * (y - x)',
        '- x * z + delta * y',
        'x * y - beta * z',
    ]
    parameters = dict(
        alpha = 36,
        beta = 3,
        delta = 20,
    )
    color = 'green4_similar_to_teal1'

    def construct(self):
        self.generate_attractor_description()#eval_functions=True, params_box_buff=0.35)


class ThreeScrollAttractorDescription(AttractorDescription):
    title = 'The Three-Scroll Unified Chaotic System Attractor'
    functions = [ 
        'a * (y - x) + delta * x * z',
        'c * x - x * z + f * y',
        'b * z + x * y - varepsilon * x**2',
    ]
    parameters = dict(
        a = 40,
        b = 1.833,
        c = 55,
        delta = 0.16,
        varepsilon = 0.65,
        f = 20,
    )
    color = 'terracota'

    def construct(self):
        self.generate_attractor_description(params_box_buff=0.24, scale_title_by=0.8)

    
class QiChenAttractorDescription(AttractorDescription):
    title = 'The Qi-Chen Attractor'
    functions = [ 
        'alpha * (y - x) + y * z',
        'zeta * x + y - x * z',
        'x * y - beta * z',
    ]
    parameters = dict(
        alpha = 38,
        beta = '8/3',
        zeta = 80,
    )
    color = 'sea_blue'

    def construct(self):
        self.generate_attractor_description()

    
class RosslerAttractorDescription(AttractorDescription):
    title = 'The Rössler Attractor'
    functions = [ 
        '- y - z',
        'x + alpha * y',
        'beta + z * (x - gamma)',
    ]
    parameters = dict(
        alpha = 0.2,
        beta = 0.2,
        gamma = 5.7,
    )
    color = 'orange_red'

    def construct(self):
        self.generate_attractor_description()

    
class FinanceAttractorDescription(AttractorDescription):
    title = 'The Finance Attractor'
    functions = [ 
        '(1 / beta - sigma) * x + z + x * y',
        '- beta * y - x **2',
        '- x - rho * z',
    ]
    parameters = dict(
        sigma = 0.001,
        beta = 0.2,
        rho = 1.1,
    )
    color = 'orange_red'

    def construct(self):
        self.generate_attractor_description()
