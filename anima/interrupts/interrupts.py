from manim import *
from manim.opengl import *

src_code = """
void main(void)
{
    init();

    while(true) {
        ...
        ...
        ...
    }
}
"""

class Test(Scene):
    def construct(self):
        line_to_renrender = ValueTracker(0)
        c = Code(
            code=src_code,
            language='c',
            insert_line_no=False,
        ).to_edge(UL)

        button = RoundedRectangle(corner_radius=0.2, width=1, height=1, color=BLUE)
        button_text = Text("btn", font_size=24).move_to(button.get_center())
        button_group = VGroup(button, button_text).shift(RIGHT*5)

        tmp = RoundedRectangle(corner_radius=0.2,
                                      width=2, height=1, color=RED, fill_color=RED,
                                      fill_opacity=.5)
        tmp_text = Text("tmp sensor", font_size=24).move_to(tmp.get_center())
        tmp_group = VGroup(tmp, tmp_text).shift(RIGHT*5 + UP*2)

        self.add(c, button_group, tmp_group)
        # for l in c.code[2:]:
        #     self.play(Indicate(l))
        buttn_msg = Text('somehow this\nbutton press\nshould be handled')
        tmp_msg = Text('somehow this\ntmp sensor request\nshould be handled and NOW')

        others = VGroup(
            VGroup(
                    Text("uart"),
                    Square(color=YELLOW)
            ),
            VGroup(
                    Text("timer"),
                    Square(color=BLUE)
            ),
            VGroup(
                    Text("adc"),
                    Square(color=PURPLE)
            ),
            VGroup(
                    Text("spi"),
                    Square(color=GREEN)
            ),
        ).arrange(RIGHT, buff=1).scale(.4).to_edge(DOWN)

        self.add(others)
        for k in range(3):
            for (i,l) in enumerate(c.code[4:9]):
                if i == 1 and k == 0:
                    self.play(Indicate(l), Indicate(button_group))
                    self.add(buttn_msg)
                    self.wait()
                    self.play(FadeOut(buttn_msg))
                elif i == 3 and k == 1:
                    self.play(Indicate(l), Indicate(tmp_group))
                    self.add(tmp_msg)
                    self.wait()
                    self.play(FadeOut(tmp_msg))
                else:
                    self.play(Indicate(l))
        t = Text('and imagine stuff\ngoing fast\nand maybe at\nthe same time')

        self.add(t)
        for item in others:
            self.play(Indicate(item), run_time=.3)
        self.play(Indicate(others))
        self.wait()



arduino_src = '''
void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
    int rb = read_from_button();
    if (overheat()) {
        ...
    }
    maybe_another_event()
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);
    delay(1000);
}
'''


class Test2(Scene):
    def construct(self):
        c = Code(
            code=arduino_src,
            language='c',
            insert_line_no=False,
        ).to_edge(UL)

        self.add(c)
        for _ in range(1):
            for (n, l) in enumerate(c.code[5:14]):
                self.play(Indicate(l, color=YELLOW if n > 4 else RED),
                          run_time= .4 if n > 4 else .8)
        questions = Text(
            '''
            What happens if you press a button and\nyour program is not actively checking for it\n(i.e., not in read_from_button())?
            '''
        ).to_edge(DR).scale(.7)
        self.play(c.animate.set_opacity(.3), Write(questions))
        c.set_opacity(1)
        self.play(Indicate(c.code[-3]))
        self.play(FadeOut(questions))
        self.wait()



src1 = '''
void main(void) {
    
    interrupts_setup();

    while (true)
    {
    
        gpio_toggle();
        
        delay();
    
    }
}
...
...
'''

class Led(OpenGLVMobject):
    def __init__(self, color=RED, label='LED-1', **kwargs):
        super().__init__(**kwargs)
        self.color=color
        self.text_handle = None
        self.container_handle=None
        self.label = label
        self.gen_shape()

    def gen_shape(self):
        self.container_handle = Circle(
            color=self.color,
            fill_opacity=1,
            stroke_color=GREEN,
            stroke_width=.8
        )
        self.text_handle = Text(self.label).next_to(self.container_handle, UP*1.5)
        self.add(self.container_handle, self.text_handle)

class Button(OpenGLVMobject):
    def __init__(self, color=BLUE, label='btn', **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.color=color
        self.text_handle = None
        self.container_handle=None
        self.gen_shape()

    def gen_shape(self):
        self.container_handle = RoundedRectangle(
            corner_radius=0.2, width=1, height=1, color=self.color)
        self.text_handle = Text(self.label).move_to(self.container_handle.get_center())
        self.add(self.container_handle, self.text_handle)


class Test3(Scene):
    def construct(self):
        c = Code(
            code=src1,
            language='c',
            insert_line_no=False
        ).to_edge(UL)
        l1 = Led().scale(.3)
        l2 = Led(color=BLUE, label='LED-2').scale(.4).shift(RIGHT*3 + DOWN*2)
        b1 = Button(color=BLUE).shift(RIGHT*3)




        self.add(c, l1, l2, b1)
        state = True
        for k in range(3):
            for (i,l) in enumerate(c.code[4:12]):
                if i == 3:
                    state = not state
                    l1.container_handle
                    self.play(Indicate(l), l1.container_handle.set_opacity(
                        1 if state else 0.2
                    ),
                        Indicate(b1), l2.container_handle.set_color(
                              PURPLE if k == 0 else GREEN
                              ),
                        run_time=1)
                else:
                    self.play(Indicate(l), run_time=.4)
        self.wait()


class GPIO(OpenGLVMobject):
    def __init__(self, label='GPIOx', **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.io_lines = VGroup()
        self.body = None
        self.label_handel = None
        self.gen_shape()
    def gen_shape(self):
        self.body = Rectangle(width=1,
                              height=2,
                              stroke_color=BLUE,
                              stroke_width=2)
        self.label_handel = Text(self.label).move_to(
            self.body.get_center()
            ).match_width(self.body).scale(.9)

        for i in range(16):
            l = Line(
                start=self.body.get_corner(UL),
                end=self.body.get_corner(UL) - LEFT
            )
            self.io_lines.add(l)
        self.io_lines.arrange(UP, buff=.1).shift(LEFT * self.body.get_width())
        self.add(self.body, self.label_handel, self.io_lines)

class EXTI(OpenGLVMobject):
    def __init__(self, label='exti', in_lines=23, out_lines=23, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.in_lines = in_lines
        self.out_lines = out_lines
        self.in_lines_handel = VGroup()
        self.out_lines_handel = VGroup()
        self.body = None
        self.label_handel = None
        self.gen_shape()
    def gen_shape(self):
        self.body = Rectangle(width=1,
                              height=3,
                              stroke_color=BLUE,
                              stroke_width=2)
        self.label_handel = Text(self.label).move_to(
            self.body.get_center()
        ).match_width(self.body).scale(.9)

        for i in range(self.in_lines):
            l = Line(
                start=self.body.get_corner(UR),
                end=self.body.get_corner(UR) + RIGHT, color=BLUE
            )
            self.in_lines_handel.add(l)
        self.in_lines_handel.arrange(UP).match_height(self.body).shift(RIGHT * self.body.get_width())


        for i in range(self.out_lines):
            l = Line(
                start=self.body.get_corner(UL),
                end=self.body.get_corner(UL) - LEFT, color=RED
            )
            self.out_lines_handel.add(l)
        self.out_lines_handel.arrange(UP).match_height(self.body).shift(LEFT * self.body.get_width())

        self.add(self.body, self.label_handel, self.in_lines_handel, self.out_lines_handel)



class Mux(OpenGLVMobject):
    def __init__(self, n_inputs, n_select, width=2, height=3, **kwargs):
        super().__init__(**kwargs)

        self.n_inputs = n_inputs
        self.n_select = n_select
        self.width = width
        self.height = height

        # Mux Body
        self.body = Polygon(
            [-width / 2, height / 3, 0],   # Top left
            [width / 2, height / 2, 0],    # Top right
            [width / 2, -height / 2, 0],   # Bottom right
            [-width / 2, -height / 3, 0],  # Bottom left
            color=WHITE
        )
        self.add(self.body)

        # Input Lines (on the right side)
        self.input_lines = VGroup()
        step = height / (n_inputs + 1)
        for i in range(n_inputs):
            y_pos = height / 2 - (i + 1) * step
            input_line = Line(
                start=[width / 2, y_pos, 0],
                end=[width / 2 + 1, y_pos, 0],
                color=BLUE
            )
            self.input_lines.add(input_line)
        self.add(self.input_lines)

        # Output Line (on the left side)
        self.output_line = Line(
            start=[-width / 2, 0, 0],
            end=[-width / 2 - 1, 0, 0],
            color=GREEN
        )
        self.add(self.output_line)

        # Vertical Select Lines (connected to body)
        self.select_lines = VGroup()
        select_spacing = width / (n_select + 1)  # Horizontal spacing for select lines
        for i in range(n_select):
            x_pos = -width / 2 + (i + 1) * select_spacing
            select_line = Line(
                start=[x_pos, -height / 2, 0],      # Start at the bottom edge of the body
                end=[x_pos, -height / 2 - 1, 0],    # Extend downward
                color=RED
            )
            self.select_lines.add(select_line)
        self.add(self.select_lines)

    def get_input_lines(self):
        return self.input_lines

    def get_output_line(self):
        return self.output_line

    def get_select_lines(self):
        return self.select_lines




class Test4(Scene):
    def construct(self):
        gpioa = GPIO(label='GPIOA')
        gpiob = GPIO(label='GPIOB')
        gpioc = GPIO(label='GPIOC')
        gpiod = GPIO(label='GPIOD')
        exti = EXTI().shift(LEFT*4)
        mux = Mux(16, 4)

        cloud = VGroup(
            Circle(radius=1.5, color=WHITE, fill_opacity=1,
                   stroke_width=0).shift(LEFT * 1.5),
            Circle(radius=1.2, color=WHITE, fill_opacity=1,
                   stroke_width=0),
            Circle(radius=1, color=WHITE, fill_opacity=1,
                   stroke_width=0).shift(RIGHT * 1.5),
            Circle(radius=1.3, color=WHITE, fill_opacity=1,
                   stroke_width=0).shift(UP * 1),
        )
        cloud2 = cloud.copy().shift(UP + RIGHT)
        cloud3 = cloud.copy().shift(RIGHT + DOWN*2)
        gpios = VGroup(
            gpioa, gpiob, gpioc, gpiod
        ).arrange(UP).scale(.7)

        gpios.shift(RIGHT*4)


        gpioa_l0_to_mux = Line(
            start=gpioa.io_lines[15].get_start(),
            end=mux.get_input_lines()[0].get_end(),
            color=BLUE
        )
        out_mux_to_in_exti0 = Line(
            start=mux.get_output_line().get_end(),
            end=exti.in_lines_handel[22].get_end(), color=GREEN
        )

        select_lines_text = Text('SYSCFG_EXTICRx').next_to(mux.get_select_lines(), DOWN)



        self.add(gpios, exti, mux, select_lines_text, cloud, cloud2, cloud3)
        self.play(FadeOut(cloud), FadeOut(cloud2), FadeOut(cloud3))
        self.play(Create(gpioa_l0_to_mux))
        self.play(Create(out_mux_to_in_exti0))
        self.wait()
        # gpioa_l0_to_mux, out_mux_to_in_exti0)


