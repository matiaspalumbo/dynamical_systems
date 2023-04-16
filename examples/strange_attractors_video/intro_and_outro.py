from manim import *
import copy

class VideoIntroWriteQuote(Scene):
    def construct(self) -> None:
        font = "Merriweather"
        quote = Text(
            '"Chaos is merely order waiting to be deciphered."',
            color='#487481',
            stroke_color='#bdc7b7',
            font=font).set_color_by_gradient('#bdc7b7', '#69a297', '#487481').scale(.55).shift(0.3*UP)
        author = Text("- José Saramago",
            color='#487481',
            stroke_color='#83adba',
            font=font).set_color_by_gradient('#69a297', '#487481').scale(.45).move_to(quote, aligned_edge=RIGHT).shift(0.6*DOWN)

        global_scale = 0.2
        snapshot_file_names = [
            ('thomas.png', None),
            ('lorentz.png', None),
            ('three_schroll.png', global_scale * 0.75),
            ('qi_chen.png', None),
            ('finance.png', global_scale * 0.75),
            ('aizawa.png', None),
            ('chen lee.png', global_scale * 0.75),
            ('chen_celikovsky.png', None),
            ('halvorsen.png', None),
            ('rossler.png', global_scale * 0.75),
        ]

        group1 = Group()
        snapshots1 = []
        for file_name, scale_factor in snapshot_file_names[:5]:
            snapshots1.append(ImageMobject(f"snapshots/cropped/{file_name}").scale(global_scale if scale_factor is None else scale_factor))
        group1 = Group(*snapshots1).arrange(RIGHT).to_edge(UP, buff=-0.2)

        group2 = Group()
        snapshots2 = []
        for file_name, scale_factor in snapshot_file_names[5:]:
            snapshots2.append(ImageMobject(f"snapshots/cropped/{file_name}").scale(global_scale if scale_factor is None else scale_factor))
        group2 = Group(*snapshots2).arrange(RIGHT, buff=0.4).to_edge(DOWN, buff=0)

        snapshots = group1.submobjects + group2.submobjects
        animations = [FadeIn(snapshot, run_time=1.18) for snapshot in snapshots]

        self.play(
            Succession(*animations),
            Succession(
                Write(quote, run_time=8),
                Wait(0.5),
                Write(author, run_time=2),
            )
        )
        self.wait(2.5)
        self.play(*[FadeOut(obj) for obj in self.mobjects], run_time=3)


class Outro(Scene):
    def construct(self):
        full_logo = SVGMobject('../../Youtube channel/svgs/full logo.svg').scale(0.25).to_corner(DR).set_color(GRAY_B)
        underline = Underline(full_logo, buff=0.1, color=GRAY_B, stroke_width=1.5).stretch(factor=1.05, dim=0)
        bye = Text("Thanks for watching!", font='Merriweather').scale(1.25).set_color_by_gradient('#d1a99d', '#ae7251', '#9c443c')

        self.play(
            Succession(
                Write(bye),
                Wait()
            )
        )
        self.play(
            FocusOn(bye),
            Succession(
                FadeIn(full_logo, run_time=1.5),
                ShowPassingFlash(underline, run_time=1.5),
                FadeOut(full_logo, run_time=1.5),
            )
        )
        self.wait(.5)
        self.play(*[FadeOut(mobj) for mobj in self.mobjects], run_time=3)