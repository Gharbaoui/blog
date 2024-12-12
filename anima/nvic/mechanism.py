from typing import Final
from ca_3b1b import *
from ca_3b1b.ic import Gear
from manimlib import *

INTERRUPT_BIT:Final = 1 << 23
NORMAL_SOURCE_CODE:Final = '''
void main(void) {
    init();
    while(1) {
        ....
        ....
        ....
    }
}
'''

ISR_SOURCE_CODE:Final = '''
void exti9_5_isr(void) {
  if (exti_get_flag_status(EXTI8)) {
    gpio_toggle(GPIOA, GPIO6);
    exti_reset_request(EXTI0 | EXTI8);
    nvic_clear_pending_irq(NVIC_EXTI0_IRQ);
  }
}
'''

class CoreFetchExecution(VMobject):
    def __init__(self,
                 irqn:int,
                 VTOR:int=0x0,
                 color=ORANGE,
                 **kwargs):
        super().__init__(*kwargs)

        self.box = Rectangle(width=2, height=1, color=color, stroke_width=.7)
        self.gear = Gear(inner_radius=.1,
                         outer_radius=.2,
                         num_teeth=4, color=color, fill_opacity=.2).move_to(
            self.box.get_corner(UR)
        )
        self.txt = Text(f'VTOR:{VTOR} + (irqn:{irqn} + 16) * 4'
                        ).match_width(self.box).scale(.8).move_to(
            self.box.get_center()
        )
        self.gear.add_updater(
                lambda obj, dt: obj.rotate(PI * dt * 6)
        )
        self.gear.suspend_updating()
        self.add(self.box, self.gear, self.txt)

class TimeLine(VMobject):
    def __init__(self,
                 time=10,
                 **kwargs):
        super().__init__(*kwargs)
        self.time_passed = 0
        self.time = time
        self.nline = NumberLine(
            x_range=(0, 14, 1),color=BLUE,include_ticks=False,include_tip=True,
        )
        self.dot = Dot().set_color(YELLOW).move_to(self.nline.number_to_point(0))
        self.add(self.nline, self.dot)

        self.dot.add_updater(
            self.move_with_time
        )

    def move_with_time(self, obj, dt):
        self.time_passed += dt
        if self.time_passed > self.time:
            self.time_passed = 0
        obj.move_to(self.nline.number_to_point(
            self.nline.x_range[1] * self.time_passed/self.time
        ))


class Intro(InteractiveScene):
    def construct(self) -> None:
        cpu_normal_execution_src = CodeBlock(
            src=NORMAL_SOURCE_CODE,
            scene=self,
            exec_animation=ExecutionAnimation(
                loop_start=2, loop_end=6, highlight_color=YELLOW
            ),
            box_color=BLUE,
        )
        t = TimeLine(time=24).to_edge(UP).shift(UP/2)
        self.add(t)
        isr_code = CodeBlock(
            src=ISR_SOURCE_CODE,
            scene=self,
            exec_animation=ExecutionAnimation(
                loop_start=0, loop_end=6, highlight_color=YELLOW,
            ),
            box_color=TEAL_D,
            code_style='rrt',
        ).scale(.7).to_edge(UR)
        nvic = VGroup()
        cpu = VGroup()
        nvic_ic = Ic(
            label='NVIC',
            left_lines=SignalLines(color=GREEN_C),
            right_lines=SignalLines(num_lines=1, color=GREEN_B),
            top_lines=SignalLines(num_lines=0),
            bottom_lines=SignalLines(num_lines=0),
            gears_attr=[
                GearAttr(
                    color=GREEN_B,
                    border_color=ORANGE,
                   fill_opacity=.75
                )
            ]
        )
        interrupt_line = nvic_ic.get_left_lines()[3]
        nvic.add(nvic_ic)

        cpu_regs = VGroup()
        cpu_regs_left = VGroup()
        cpu_regs_right = VGroup()
        cpu_reg_xpsr = Register(
            word_data=WordData(value=0x1000000, opacity=0.1),
            label='xpsr',dir=Direction.LEFT
        )
        cpu_reg_pc = Register(
            word_data=WordData(value=0x8000208, opacity=.1),
            label='pc',dir=Direction.LEFT
        )
        cpu_reg_lr = Register(
            word_data=WordData(value=0x8000205, opacity=.1),
            label='lr',dir=Direction.LEFT
        )
        cpu_reg_r12 = Register(
            word_data=WordData(value=0x20, opacity=.1),
            label='r12',dir=Direction.LEFT
        )

        cpu_reg_r3 = Register(
            word_data=WordData(value=0xe000e100, opacity=.1),
            label='r3',dir=Direction.LEFT
        )
        cpu_reg_r2 = Register(
            word_data=WordData(value=0x800000, opacity=.1),
            label='r2',dir=Direction.LEFT
        )
        cpu_reg_r1 = Register(
            word_data=WordData(value=0x10, opacity=.1),
            label='r1',dir=Direction.LEFT
        )
        cpu_reg_r0 = Register(
            word_data=WordData(value=0x40020000, opacity=.1),
            label='r0',dir=Direction.LEFT
        )

        cpu_regs_left.add(cpu_reg_xpsr, cpu_reg_pc, cpu_reg_lr, cpu_reg_r12)
        cpu_regs_left.arrange(DOWN)
        cpu_regs_right.add(cpu_reg_r3, cpu_reg_r2, cpu_reg_r1, cpu_reg_r0)
        cpu_regs_right.arrange(DOWN)
        cpu_regs.add(cpu_regs_left, cpu_regs_right)
        cpu_regs.scale(.4)
        cpu_regs.arrange(RIGHT).to_edge(DL)
        cpu_reg_box = SurroundingRectangle(cpu_regs, color=BLUE_D, stroke_width=.7)
        cpu_regs.add(cpu_reg_box)

        cpu_ic  = Ic(
            width=1, height=1,
            label='core',
            left_lines=SignalLines(color=BLUE_A),
            right_lines=SignalLines(num_lines=0, color=GREEN_B),
            top_lines=SignalLines(num_lines=0),
            bottom_lines=SignalLines(num_lines=0),
            gears_attr=[
                GearAttr(),
                GearAttr(
                    color=GREEN_B,
                    border_color=ORANGE,
                    fill_opacity=.75,
                    pos=DL
                ),
                GearAttr(
                    color=TEAL_E,
                    border_color=TEAL_A,
                    fill_opacity=.8,
                    pos=DR
                )
            ]
        ).to_edge(RIGHT, buff=2.5)
        cpu_normal_execution_src.next_to(cpu_ic, RIGHT)
        cpu_normal_execution_src.set_updaters()
        cpu.add(cpu_ic, cpu_normal_execution_src)

        nvic_regs = VGroup()
        nvic_pending_register = Register(
            word_data=WordData(
                value=0x0,
                data_format=DataFormat.BIN,
                color=TEAL_B, opacity=.2,
                border_color=TEAL_C
            ),
            label='NVIC_ISPRx', dir=Direction.LEFT
        )
        nvic_enable_register = Register(
            word_data=WordData(
                value=INTERRUPT_BIT,
                data_format=DataFormat.BIN,
                color=TEAL_B, opacity=.2,
                border_color=TEAL_C
            ),
            label='NVIC_ISER', dir=Direction.LEFT
        )
        enable_bit = nvic_enable_register.get_word().get_byte(1).value_txt[0]
        
        nvic_regs.add(nvic_pending_register, nvic_enable_register)
        nvic_regs.scale(.5)
        nvic_regs.arrange(DOWN).to_edge(DL)
        nvic_sur_rect = SurroundingRectangle(nvic_regs)
        nvic_regs.add(nvic_sur_rect) 
        nvic_regs.next_to(nvic_ic, DOWN)

        nvic.add(nvic_regs)
        nvic.to_edge(LEFT, buff=2.5)

        self.add(nvic, cpu)

        cpu_ic.resume(0)
        self.wait(2)
        nvic_ic.resume(0)
        self.play(Indicate(interrupt_line, color=RED_D), run_time=1)
        nvic_pending_register.get_word().update_value(INTERRUPT_BIT)
        pending_bit = nvic_pending_register.get_word().get_byte(1).value_txt[0]
        self.play(Indicate(pending_bit, color=RED,scale_factor=4), run_time=1)
        pending_bit.set_color(RED)
        pending_bit_cp = copy.deepcopy(pending_bit)
        enable_bit_cp = copy.deepcopy(enable_bit)
        self.embed()
        
        REF:Final = nvic_regs.get_corner(DL) + DOWN
        and_txt = Text("and").move_to(REF + RIGHT)
        assumtion_txt_1 = Text(
            "assume other registers are valid like priority registers..."
        ).scale(.35).move_to(REF + 3 * RIGHT + DOWN/2)
        self.play(
            pending_bit_cp.animate.move_to(REF).scale(4.5),
            Write(and_txt),
            enable_bit_cp.animate.move_to(REF + 2 * RIGHT).scale(4.5),
            Write(assumtion_txt_1),
            lag_ratio=0.5,
            run_time=3,
        )
        all_v1 = VGroup(pending_bit_cp, enable_bit_cp, and_txt, assumtion_txt_1)
        true_txt = Text("True i.e let's interrupt the core").set_color(GREEN).scale(.7).move_to(REF + 2*RIGHT)
        self.play(Transform(all_v1, true_txt), run_time=2)
        self.wait(.5)
        connection_between_nvic_and_cpu = always_redraw(lambda: Line(
            start=nvic_ic.get_right_lines()[0].get_start(),
            end=cpu_ic.get_left_lines()[3].get_end(), color=[GREEN, TEAL_B]
        ))
        self.play(nvic_regs.animate.next_to(nvic_ic, UP), run_time=.3)
        self.play(
            nvic.animate.to_edge(UL),
            cpu.animate.next_to(nvic_ic).shift(LEFT),
            ShowCreation(connection_between_nvic_and_cpu),
            run_time=2
        )
        self.play(FadeOut(all_v1), run_time=.4)
        nvic_irqn_to_cpu_indicator = LabeledDot(color=ORANGE, label='23').scale(.4).move_to(
            connection_between_nvic_and_cpu.get_start())
        self.add(nvic_irqn_to_cpu_indicator)
        self.play(
            nvic_irqn_to_cpu_indicator.animate.move_to(
                connection_between_nvic_and_cpu.get_end()), run_time=.4
        )
        self.play(
            nvic_irqn_to_cpu_indicator.animate.move_to(
                cpu_ic.get_left_lines()[3].get_start()
            ),
            run_time=.4
        )
        cpu.add(nvic_irqn_to_cpu_indicator)
        # self.play(FadeOut(nvic_irqn_to_cpu_indicator), run_time=.2)
        nvic_ic.suspend(0)
        # self.wait(4)
        cpu_showing_regs = always_redraw(lambda: Polygon(
            *[
                cpu_ic.body.get_corner(DL),
                cpu_ic.body.get_corner(DR),
                cpu_reg_box.get_corner(UR),
                cpu_reg_box.get_corner(UL)
            ],
            color=BLUE,
            fill_opacity=.2,
            stroke_width=.4,
        ))
        cpu_showing_regs.z_index=-1

        self.play(
            cpu_normal_execution_src.animate.scale(.7).next_to(cpu_ic, UP),
            FadeIn(cpu_regs), ShowCreation(cpu_showing_regs)
        )

        mem = Memory(
           start_address=0x2001ffe8,size=8 * 5, mem_dir=Direction.DOWN, addr_dir=Direction.LEFT
        ).scale(.3).to_edge(DOWN).shift(RIGHT + DOWN/4)
        
        self.play(ShowCreation(mem))
        ## now stacking will start
        cpu_reg_xpsr_cp = copy.deepcopy(cpu_reg_xpsr)
        cpu_reg_pc_cp = copy.deepcopy(cpu_reg_pc)
        cpu_reg_lr_cp = copy.deepcopy(cpu_reg_lr)
        cpu_reg_r12_cp = copy.deepcopy(cpu_reg_r12)
        cpu_reg_r3_cp = copy.deepcopy(cpu_reg_r3)
        cpu_reg_r2_cp = copy.deepcopy(cpu_reg_r2)
        cpu_reg_r1_cp = copy.deepcopy(cpu_reg_r1)
        cpu_reg_r0_cp = copy.deepcopy(cpu_reg_r0)
        # self.add(
        #     cpu_reg_xpsr_cp, cpu_reg_pc_cp, cpu_reg_lr_cp, cpu_reg_r12_cp, cpu_reg_r3_cp,
        #     cpu_reg_r2_cp, cpu_reg_r1_cp, cpu_reg_r0_cp
        # )


        current_regs_to_transform = [
            cpu_reg_xpsr_cp, cpu_reg_pc_cp, cpu_reg_lr_cp, cpu_reg_r12_cp,
            cpu_reg_r3_cp, cpu_reg_r2_cp, cpu_reg_r1_cp, cpu_reg_r0_cp
        ]
        values = [
            0x1000000,
            0x8000208,
            0x8000205,
            0x100,
            0xe000e100,
            0x800000,
            0x20,
            0x40020000,
        ]
        address_start = 0x2001ffe4

        cpu_ic.suspend(0)
        cpu_ic.resume(1)

        cfe = CoreFetchExecution(23).scale(.7).next_to(cpu_normal_execution_src, RIGHT)
        cfe_txt_result = Text('0x0000009c').match_width(cfe.txt).move_to(cfe.txt.get_center())
        vector_table = Memory(
            start_address=0x0000008c, size=4*9,
            word_data=WordData(
                value=None,
               color=ORANGE, opacity=.2, border_color=YELLOW_E 
            ),
            addr_dir=Direction.LEFT
        ).scale(.4).to_edge(DR)
        vector_table.set_value_at(0x0000009c, 0x08000220)
        pointer_to_vt = Arrow(
                stroke_width=.7,
                start=cfe.get_corner(DR),
                end=vector_table.get_word_at(0x9c)[1].get_center() + LEFT/2).set_color(YELLOW_E)

        self.add(vector_table ,cfe, isr_code)
        cfe.gear.resume_updating()

        for i in range(len(values)):
            if i == 5:
                self.play(Transform(cfe.txt, cfe_txt_result), run_time=.2)
            elif i == 6:
                self.play(ShowCreation(pointer_to_vt), run_time=.2)
            self.play(mem.animate.set_value_at(address_start, values[i]), run_time=.2)
            self.play(Transform(current_regs_to_transform[i], mem.get_word_at(address_start)), run_time=.5)
            address_start -= 4
        isr_entry_cp = copy.deepcopy(vector_table.get_word_at(0x9c)[0])
        self.play(
            FadeOut(cpu_reg_pc.get_word()),
            isr_entry_cp.animate.move_to(cpu_reg_pc.get_word().get_center())
        )
        pc_to_isr_pointer = Arrow(
                start=isr_entry_cp.get_center(),
                end=isr_code.get_corner(UL),
                color=TEAL_E).set_color(TEAL_D)
        self.add(pc_to_isr_pointer)
        cpu_ic.resume(2)
        cpu_ic.suspend(1)
        isr_code.set_updaters()
        nvic_pending_register.get_word().update_value(0x0)
        pending_bit = nvic_pending_register.get_word().get_byte(1).value_txt[0]
        self.play(Indicate(pending_bit, color=ORANGE,scale_factor=4), run_time=.3)

        isr_code.resume()
        self.wait(.1)
        isr_code.stop()
        cpu_ic.suspend(2)
        self.wait(2)

        to_remove_from_scene = [
            nvic, connection_between_nvic_and_cpu, pc_to_isr_pointer,
            cfe, vector_table, pointer_to_vt
        ]
        self.play(*[FadeOut(obj) for obj in to_remove_from_scene])
        
        nvic_irqn_to_cpu_indicator.z_index=10
        self.play(
            cpu.animate.to_edge(LEFT)
        )
        isr_code.resume()
        cpu_ic.resume(2)
        cpu_reg_lr.get_word().update_value(0xfffffff9)
        self.wait(2.5)
        
        cpu_reg_xpsr.get_word().update_value(0x21000027)
        cpu_reg_r12.get_word().update_value(0x100)
        cpu_reg_r3.get_word().update_value(0x40013000)
        cpu_reg_r2.get_word().update_value(0x0)
        cpu_reg_r1.get_word().update_value(0x40)
        cpu_reg_r0.get_word().update_value(0x100)
        isr_code.stop()
        cpu_ic.suspend(2)
        self.wait(.5)

        current_regs_to_target = [
            cpu_reg_xpsr, cpu_reg_pc, cpu_reg_lr, cpu_reg_r12,
            cpu_reg_r3, cpu_reg_r2, cpu_reg_r1, cpu_reg_r0
        ]

        for value, from_reg, to in zip(reversed(values), reversed(current_regs_to_transform),
                                   reversed(current_regs_to_target)):
            to.get_word().update_value(value)
            self.play(Transform(from_reg, to))
        self.remove(isr_entry_cp)
        cpu_ic.resume(0)
        cpu_normal_execution_src.resume()
        # question_how_should_we_go_back = Text('''
        # How should we return to normal execution?
        # ''')
        # # update value of registers
        # self.play(Indicate(question_how_should_we_go_back))
        self.wait(4)

        
        self.embed()



class Test(InteractiveScene):
    def construct(self) -> None:
        ct = CodeBlock(
            src=NORMAL_SOURCE_CODE,
            scene=self,
            exec_animation=ExecutionAnimation(
                loop_start=2, loop_end=6, highlight_color=YELLOW,exec_speed=1
            ),
            box_color=BLUE,
        )

        self.add(ct)
        ct.set_updaters()
        ct.resume()
        self.wait(5)
        self.embed()
