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
            # group1.add()
        group1 = Group(*snapshots1).arrange(RIGHT).to_edge(UP, buff=-0.2)

        group2 = Group()
        snapshots2 = []
        for file_name, scale_factor in snapshot_file_names[5:]:
            snapshots2.append(ImageMobject(f"snapshots/cropped/{file_name}").scale(global_scale if scale_factor is None else scale_factor))
            # group2.add()
        group2 = Group(*snapshots2).arrange(RIGHT, buff=0.4).to_edge(DOWN, buff=0)

        snapshots = group1.submobjects + group2.submobjects
        # snapshots = [copy.deepcopy(snapshot) for snapshot in snapshots1 + snapshots2]

        # for snapshot in snapshots:
        #     self.play(FadeIn(snapshot), run_time=1.5)
        animations = [FadeIn(snapshot, run_time=1.05) for snapshot in snapshots]
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
        # self.add(group1, group2)




        # self.play(Write(quote), run_time=11)
        # self.wait()
        # self.play(Write(author), run_time=3)
        # self.wait(2.5)


class VideoIntroFadeSnapshots(Scene):
    def construct(self) -> None:
        snapshot_file_names_manimgl = [
            ('thomas.png', None),
            ('lorentz.png', None),
            ('three_schroll.png', 0.575),
            ('qi_chen.png', None),
            ('finance.png', 0.6),
            ('aizawa.png', None),
            ('chen lee.png', 0.6),
            ('chen_celikovsky.png', None),
            ('halvorsen.png', None),
            ('rossler.png', 0.65),
        ]
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
            # group1.add()
        group1 = Group(*snapshots1).arrange(RIGHT).to_edge(UP, buff=0)

        group2 = Group()
        snapshots2 = []
        for file_name, scale_factor in snapshot_file_names[5:]:
            snapshots2.append(ImageMobject(f"snapshots/cropped/{file_name}").scale(global_scale if scale_factor is None else scale_factor))
            # group2.add()
        group2 = Group(*snapshots2).arrange(RIGHT, buff=0.4).to_edge(DOWN, buff=0.1)

        snapshots = group1.submobjects + group2.submobjects
        # snapshots = [copy.deepcopy(snapshot) for snapshot in snapshots1 + snapshots2]

        # for snapshot in snapshots:
        #     self.play(FadeIn(snapshot), run_time=1.5)
        animations = [FadeIn(snapshot, run_time=0.1) for snapshot in snapshots[:3]]
        # self.play(Succession(*animations))
        self.add(group1)

