from manim import *
import numpy as np
import IPython
from manim.opengl import *


class CustomAxes(Mobject):
    def __init__(self, x_range=(-5, 5), y_range=(-5, 5), color=BLUE, x_length=5, y_length=5, **kwargs):
        super().__init__(**kwargs)
        self.x_range=x_range
        self.y_range=y_range
        self.color=color
        self.x_length = x_length
        self.y_length = y_length
        self.axes = None
        self.unit_vectors = []
        self.vectors = []
        self.x_unit_length = 1
        self.y_unit_length = 1
        self.plane = None
        self.create_axes()
        self.create_unit_vectors()


    def init_vars(self):
        self.x_unit_length = np.linalg.norm(
                self.axes.c2p(1, 0) - self.axes.c2p(0, 0)
                )
        self.y_unit_length = np.linalg.norm(
                self.axes.c2p(0, 1) - self.axes.c2p(0, 0)
                )

    @property
    def x_unit_len(self):
        return self.x_unit_length
    @property
    def y_unit_len(self):
        return self.y_unit_length


    def create_axes(self):
        self.axes = Axes(
            x_range=self.x_range, y_range=self.y_range,
            axis_config={"color":self.color},
            x_length=self.x_length,
            y_length=self.y_length
        )
        self.plane = NumberPlane(
            x_range=self.x_range, y_range=self.y_range,
            x_length=self.x_length,
            y_length=self.y_length,
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 4,
                "stroke_opacity": 0.4
            }
        )
        self.init_vars()
        self.add(self.axes)

    def get_plane(self):
        self.plane.move_to(self.axes.c2p(0, 0))
        return self.plane
            


    def add_vector(self, pos, name="v", color=YELLOW):
        l = Line(
            start=self.axes.c2p(0, 0),
            end=self.axes.c2p(*pos),
            color=color, tip_length=0.15
        ).add_tip()

        l.set_opacity(.8)
        l_tex = MathTex(name, color=color).move_to(l.get_center()+DOWN/8).scale(0.7)
        self.vectors.append(VGroup(l, l_tex))
        self.add(self.vectors[-1])

    def c2p(self, pos):
        return self.axes.c2p(*pos)

    def create_unit_vectors(self):
        # i_vec = Vector(self.axes.c2p(1, 0), color=RED)
        i_vec = Line(
            start=self.axes.c2p(0, 0),
            end=self.axes.c2p(1, 0),
            color=RED, tip_length=0.15
        ).add_tip()

        i_tex = MathTex("\\hat{\\imath}", color=RED).next_to(i_vec, DOWN/12).scale(0.5)
        j_vec = Line(
            start=self.axes.c2p(0, 0),
            end=self.axes.c2p(0, 1),
            color=GREEN, tip_length=0.15
        ).add_tip()


        j_tex = MathTex("\\hat{\\jmath}", color=GREEN).next_to(i_vec, UL/4).scale(0.5)
        self.unit_vectors.extend([VGroup(i_vec, i_tex), VGroup(j_vec, j_tex)])
        self.add(*self.unit_vectors)

class OpenGl2D(Scene):
    def construct(self):
        axes1 = CustomAxes()
        d = Dot().move_to(axes1.c2p([2, 1]))
        axes1.add_vector([2, 1])
        self.add(axes1, d)
        self.interactive_embed()




class CustomAxes3D(VMobject):
    def __init__(self, x_range=(-5, 5), y_range=(-5, 5), z_range=(-5, 5), color=BLUE, x_length=5, y_length=5, z_length=5, **kwargs):
        super().__init__(**kwargs)
        self.x_range=x_range
        self.y_range=y_range
        self.z_range=z_range
        
        self.color=color
        
        self.x_length = x_length
        self.y_length = y_length
        self.z_length = z_length
        
        self.axes = None
        self.unit_vectors = []
        self.vectors = []
        
        self.x_unit_length = 1
        self.y_unit_length = 1
        self.z_unit_length = 1

        self.xy_plane = None
        self.xz_plane = None
        self.yz_plane = None


        self.current_orientation = np.array([])

        self.create_axes()
        self.create_unit_vectors()


    def init_vars(self):
        self.x_unit_length = np.linalg.norm(
                self.axes.c2p(1, 0, 0) - self.axes.c2p(0, 0, 0)
                )
        self.y_unit_length = np.linalg.norm(
                self.axes.c2p(0, 1, 0) - self.axes.c2p(0, 0, 0)
                )
        self.z_unit_length = np.linalg.norm(
                self.axes.c2p(0, 0, 1) - self.axes.c2p(0, 0, 0)
                )
        self.current_orientation = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
            ])


    @property
    def x_unit_len(self):
        return self.x_unit_length
    @property
    def y_unit_len(self):
        return self.y_unit_length
    @property
    def z_unit_len(self):
        return self.z_unit_length


    def create_axes(self):
        self.axes = ThreeDAxes(
            x_range=self.x_range, y_range=self.y_range,z_range=self.z_range,
            axis_config={"color":self.color},
            x_length=self.x_length,
            y_length=self.y_length,
            z_length=self.z_length
        )
        self.init_vars()

        self.xy_plane = NumberPlane(
            x_range=self.x_range, y_range=self.y_range,
            x_length=self.x_length,
            y_length=self.y_length,
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 4,
                "stroke_opacity": 0.4
            }
        )

        self.xz_plane = NumberPlane(
            x_range=self.x_range, y_range=self.z_range,
            x_length=self.x_length,
            y_length=self.z_length,
            background_line_style={
                "stroke_color": ORANGE,
                "stroke_width": 4,
                "stroke_opacity": 0.4
            }
        )
        self.xz_plane.apply_matrix(np.array([
            [1, 0, 0],
            [0, np.cos(PI/2), np.sin(PI/2)],
            [0, -np.sin(PI/2), np.cos(PI/2)]
            ]))

        self.zy_plane = NumberPlane(
            x_range=self.z_range, y_range=self.y_range,
            x_length=self.z_length,
            y_length=self.y_length,
            background_line_style={
                "stroke_color": PINK,
                "stroke_width": 4,
                "stroke_opacity": 0.4
            }
        )
        self.zy_plane.apply_matrix(np.array([
            [np.cos(PI/2), 0, -np.sin(PI/2)],
            [0, 1, 0],
            [np.sin(PI/2), 0, np.cos(PI/2)]
            ]))


        self.add(self.axes)

    def add_vector(self, pos, name="v", color=YELLOW, normlized=False):
        if normlized == True:
            pos = pos/np.linalg.norm(pos)
        l = Line(
            start=self.axes.c2p(0, 0, 0),
            end=self.axes.c2p(*pos),
            color=color, tip_length=0.15
        ).add_tip()

        l.set_opacity(0.8)
        l_tex = MathTex(name, color=color).move_to(l.get_center()+DOWN/8).scale(0.7)
        self.vectors.append(VGroup(l, l_tex))
        self.add(self.vectors[-1])



    def c2p(self, pos):
        return self.axes.c2p(*pos)

    def reset_rot(self):
        rot_mat = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
            ])

        self.apply_matrix(rot_mat)


    def rot_about_y(self, angle):
        rot_mat = np.array([
            [np.cos(angle), 0, -np.sin(angle)],
            [0, 1, 0],
            [np.sin(angle), 0, np.cos(angle)]
            ])


        self.current_orientation = np.matmul(rot_mat, self.current_orientation)
        self.apply_matrix(rot_mat)

    def rot_about_x(self, angle):
        rot_mat = np.array([
            [1, 0, 0],
            [0, np.cos(angle), np.sin(angle)],
            [0, -np.sin(angle), np.cos(angle)]
            ])

        self.current_orientation = np.matmul(rot_mat, self.current_orientation)
        self.apply_matrix(rot_mat)

    def rot_about_z(self, angle):
        rot_mat = np.array([
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)]
            ])

        self.current_orientation = np.matmul(rot_mat, self.current_orientation)
        self.apply_matrix(rot_mat)

    def create_unit_vectors(self):
        # i_vec = Vector(self.axes.c2p(1, 0), color=RED)
        i_vec = Line(
            start=self.axes.c2p(0, 0, 0),
            end=self.axes.c2p(1, 0, 0),
            color=RED, tip_length=0.15
        ).add_tip()

        i_tex = MathTex("\\hat{\\imath}", color=RED).next_to(i_vec, DOWN/12).scale(0.5)

        j_vec = Line(
            start=self.axes.c2p(0, 0, 0),
            end=self.axes.c2p(0, 1, 0),
            color=GREEN, tip_length=0.15
        ).add_tip()

        j_tex = MathTex("\\hat{\\jmath}", color=GREEN).next_to(i_vec, UL/4).scale(0.5)

        k_vec = Line(
            start=self.axes.c2p(0, 0, 0),
            end=self.axes.c2p(0, 0, 1),
            color=GREEN, tip_length=0.15
        ).add_tip()
        # k_tex = MathTex("\\hat{\\kmath}", color=GREEN).next_to(i_vec, UL/4).scale(0.5)


        self.unit_vectors.extend([VGroup(i_vec, i_tex), VGroup(j_vec, j_tex), VGroup(k_vec,)])
        self.add(*self.unit_vectors)

    def gen_line(self, p1, p2, length=1, color=YELLOW):
        dir_vec = np.array(p2) - np.array(p1)
        gen_point = dir_vec*length
        return Line (start=p1, end=gen_point, color=color)

    def get_plane(self):
        return VGroup(self.zy_plane, self.xy_plane, self.xz_plane)



class OpenGl3D(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(zoom=.75)
        background_axes = CustomAxes3D(
                            color=PINK
                            )
        
        background_axes.set_opacity(0.2)
        
        all = VGroup()

        screen = VGroup()
        surface = Surface(
            lambda u, v: [u, v, 4*background_axes.z_unit_len],
            u_range=[-4 * background_axes.x_unit_len, 4 * background_axes.x_unit_len],
            v_range=[-3 * background_axes.y_unit_len, 3 * background_axes.y_unit_len], resolution=(40, 30)
        )
        surface.move_to(background_axes.c2p([0,0, 16 * background_axes.z_unit_len]))

        screen.add(surface)

    
        # CAMERA
        camera = VGroup()
        camera_axes = CustomAxes3D(x_range=(-1,1), y_range=(-1,1), z_range=(-10,1), x_length=1, y_length=1, z_length=8)
        cube = Cube(camera_axes.x_unit_len/4, color=BLUE_B)
        camera.add(camera_axes, cube)
        camera.move_to(background_axes.c2p([0, 0, 7]))
        
        # camera lines

        camera_lines = VGroup()
        top_right = Line(
            start=camera_axes.c2p([0, 0, 0]), end=((surface.get_corner(UR) - camera_axes.c2p([0, 0, 0])) * 1 + surface.get_corner(UR)), color=YELLOW
        )

        top_left = Line(
            start=camera_axes.c2p([0, 0, 0]), end=((surface.get_corner(UL) - camera_axes.c2p([0, 0, 0])) * 1 + surface.get_corner(UL)), color=YELLOW
        )
        bottom_right = Line(
            start=camera_axes.c2p([0, 0, 0]), end=((surface.get_corner(DR) - camera_axes.c2p([0, 0, 0])) * 1 + surface.get_corner(DR)), color=BLUE
        )

        bottom_left = DashedLine(
            start=camera_axes.c2p([0, 0, 0]), end=((surface.get_corner(DL) - camera_axes.c2p([0, 0, 0])) * 1 + surface.get_corner(DL)), color=BLUE
        )

        camera_lines.add(top_right, top_left, bottom_right, bottom_left)
        camera.add(camera_lines)

        world = VGroup()
        obj1 = Cube(side_length=background_axes.x_unit_len)
        obj1.set_color(MAROON_D)
        obj1.move_to(background_axes.c2p([2, 2, -3]))

        obj2 = Cylinder(radius=background_axes.x_unit_len, height=3*background_axes.y_unit_len)
        obj2.set_color(GOLD_E)
        obj2.move_to(background_axes.c2p([-3, 3, -1]))
        bottom_center_point_pos = [-4, 2, -8]
        bottom_center_point = Dot3D(color=RED).move_to(camera_axes.c2p(bottom_center_point_pos))
        bottom_center_point_pos_text = get_vec_text(bottom_center_point_pos, bottom_center_point)

        projected_point_line = Line(
            start=camera_axes.c2p([0, 0, 0]), end=bottom_center_point.get_center(), color=WHITE
        )

        point = VGroup(bottom_center_point, bottom_center_point_pos_text, projected_point_line)
        
        projected_point = point.copy()
        projected_point.remove(-1)

        near_plane_pos = [0,0, -4]
        surface.move_to(camera_axes.c2p(near_plane_pos))
        

        world.add(obj1, obj2, point)
        all.add(background_axes, camera, surface, world, projected_point)
        # angle = PI/3
        # all.apply_matrix(
        #     np.array([
        #     [np.cos(angle), 0, -np.sin(angle)],
        #     [0, 1, 0],
        #     [np.sin(angle), 0, np.cos(angle)]
        #     ])
        # )
        # all.to_edge(UP + RIGHT/8)
        camera_lines.set_opacity(0.3)
        # all.rotate(-PI/2, axis=UP, about_point=ORIGIN)
        all.rotate(-PI/5, axis=UP, about_point=ORIGIN)
        all.rotate(PI/5, axis=RIGHT, about_point=ORIGIN+OUT)
        all.shift(RIGHT + UP)
        self.add(all)

        # self.add(Text("Side-View").to_edge(DL))
        stats = VGroup()
        near_plane_z_value = Tex(f"n: {near_plane_pos[-1]}")
        stats.add(near_plane_z_value)
        stats.to_edge(UL)
        self.add(stats)

        new_pos = get_projected_point_m1(-near_plane_pos[2], bottom_center_point_pos)
        self.wait(1)
        projected_point[0].set_color(GREEN)

        self.play(projected_point[0].
                  animate.move_to(camera_axes.c2p(new_pos)),
                #   projected_point[1].
                #   animate.move_to(camera_axes.c2p(new_pos)),
                  Transform(projected_point[1],  get_vec_text(new_pos, projected_point[0]).set_color(BLACK).move_to(camera_axes.c2p(new_pos))),
                  run_time=2, rate_func=linear)
        self.wait()
        self.play(Rotate(all, angle=-PI/5, axis=RIGHT, about_point=ORIGIN+OUT), run_time=1)
        self.play(Rotate(all, about_point=ORIGIN, axis=UP, angle=PI), run_time=2)
        self.wait()

        # print()

        # self.play(all.animate.rotate(-PI/3, axis=UP, about_point=ORIGIN), run_time=2.5, rate_func=linear)
        # self.wait(1)


def get_projected_point_m1(near, pos):
    return np.array([
        -near*pos[0]/pos[2],
        -near*pos[1]/pos[2],
        -near
    ])

def get_vec_text(pos, next_to_pos):
    return MathTex(r"\vec{v} = \begin{bmatrix}"
                                               f"{pos[0]}" " \\\ " f"{pos[1]}" " \\\ " f"{pos[2]}"
                                               "\end{bmatrix}").next_to(next_to_pos, UP/8).scale(.5)


class AspectRatio(ThreeDScene):
    def construct(self):
        ref_axes = CustomAxes3D()

        camera = VGroup()
        camera_axes = CustomAxes3D(x_range=(-1,1), y_range=(-1,1), z_range=(-10,1), x_length=1, y_length=1, z_length=8)
        cube = Cube(camera_axes.x_unit_len/4, color=BLUE_B)
        camera.add(camera_axes, cube)
        camera.move_to(ref_axes.c2p([0, 0, 7]))

        screen = VGroup()
        screen_pixels = Surface(
            lambda u, v: [u, v, 0], u_range=[-4, 4], v_range=[-2,2], resolution=(8, 4), fill_opacity=.75
        ).scale(3/4)

        screen_axes = Axes(
            x_range=screen_pixels.u_range,
            y_range=screen_pixels.v_range,
            x_length=screen_pixels.width,
            y_length=screen_pixels.height,
            axis_config={"color":BLACK}
        )
        screen.add(screen_pixels, screen_axes)
        screen.move_to(camera_axes.c2p([0,0,-5]))

        world = VGroup()
        
        obj1 = VGroup(Cube(side_length=screen_pixels.width/8).move_to(camera_axes.c2p([0,0,-8])))
        

        cube_to_camera_lines = VGroup(
            Line(
                start=obj1[0].get_corner(UP+RIGHT+OUT), end=camera_axes.c2p([0,0,0]), color=YELLOW,
            ),
            Line(
                start=obj1[0].get_corner(DOWN+RIGHT+OUT), end=camera_axes.c2p([0,0,0]), color=YELLOW,
            ),
            Line(
                start=obj1[0].get_corner(UP+LEFT+OUT), end=camera_axes.c2p([0,0,0]), color=YELLOW,
            ),
            Line(
                start=obj1[0].get_corner(DOWN+LEFT+OUT), end=camera_axes.c2p([0,0,0]), color=YELLOW,
            )
        )

        cube_space = NumberPlane(
            x_range=screen_pixels.u_range,
            y_range=screen_pixels.v_range,
            x_length=screen_pixels.width,
            y_length=screen_pixels.width,
        ).move_to(obj1[0].get_center())

        obj1.add(cube_to_camera_lines, cube_space)
        

        world.add(obj1)

        all = VGroup(
            camera, 
            world,
            screen,
        )

        all.rotate(-PI/4, axis=UP, about_point=ORIGIN)
        all.rotate(PI/4, axis=RIGHT, about_point=ORIGIN+ 2*OUT)
        
        self.add(all)
        
        self.play(
            Rotate(all, angle=-PI/4, axis=RIGHT, about_point=ORIGIN + 2 * OUT),
        )
        self.play(
            Rotate(all, angle=PI/4, axis=UP, about_point=ORIGIN)
        )

        self.play(FadeOut(camera),  
                  screen.animate.scale(1/2),
                  obj1.animate.scale(1/2),
        )
        
        
        self.play(
            screen.animate.shift(2* LEFT), obj1.animate.shift(2 * RIGHT), FadeOut(cube_to_camera_lines)
        )

        self.play(
            Write(Tex("screen pixels").next_to(screen, UP)), Write(Tex("NDC").next_to(obj1, UP))
        )


        self.wait()
        self.play(Write(Text("cube scale Just to Make math easy").to_edge(DOWN)))
        self.play(obj1[0].animate.scale_to_fit_width(cube_space.x_length/8))
        self.wait()
        self.play(obj1[0].animate.set_color(YELLOW))
        self.wait()




class AspectRatioEx(Scene):
    def construct(self):
        
        screen_pixels = Surface(
            lambda u, v: [u, v, 0], u_range=[-4, 4], v_range=[-2,2], resolution=(8, 4)
        ).scale(1/2).shift(3 * LEFT)

        num = NumberPlane(
            x_range=[-4, 4, 1], y_range=[-2, 2, 1], x_length=4, y_length=4
        ).shift(3 * RIGHT)

        sq = Rectangle(
            width=2, height=4,fill_color=YELLOW, fill_opacity=.75
        ).shift(3 * RIGHT)

        final_rect = Rectangle(width=2, height=2, fill_color=YELLOW, fill_opacity=.75).move_to(screen_pixels.get_center())

        self.add(screen_pixels, num, sq)
        self.wait()
        self.play(Transform(sq, final_rect))
        self.wait()
        self.play(
            FadeOut(num),
            screen_pixels.animate.shift(3*RIGHT),
            sq.animate.shift(3*RIGHT),
        )
        self.play(
            screen_pixels.animate.scale(2),
            sq.animate.scale(2)
        )
        self.wait()
        


class ShowZAxis(Scene):
    def construct(self):
        axes = Axes(x_range=[-10, 1], y_range=[-4, 4], axis_config={"color": BLUE})
        
        axes.rotate(PI, axis=OUT, about_point=ORIGIN)
        axes.rotate(PI, axis=RIGHT, about_point=ORIGIN)

        rect1 = Rectangle(width=1, height=2, color=BLUE, fill_color=PURPLE, fill_opacity=.75).move_to(axes.c2p(-5))
        slope = (rect1.get_corner(UL)[1] - axes.c2p(0, 0)[1]) / (rect1.get_corner(UL)[0] - axes.c2p(0, 0)[0])
        
        diff = 3
        rect2 = Rectangle(width=1, height=((rect1.width + diff)*slope * 1.5) + rect1.height, color=RED, fill_color=RED_B, fill_opacity=.75).move_to(rect1.get_center() + RIGHT*diff)

        vert_line = Line(
            start=axes.c2p(-2, -3), end=axes.c2p(-2, 3), color=WHITE
        )

        def projec_line_eq(x):
            return -slope*x
        projection_line = Line(start=axes.c2p(0, 0), end=rect2.get_corner(UL), color=YELLOW)
        rect1_dot = Dot(color=RED).move_to(rect1.get_corner(UL))
        rect2_dot = Dot(color=GREEN).move_to(rect2.get_corner(UL))
        pos = axes.c2p(-2, 0)
        pos[1] = projec_line_eq(-2)
        projected_point = Dot(color=BLUE).move_to(pos)

        self.add(axes, rect1, rect2, projection_line, vert_line)
        self.add(rect1_dot , rect2_dot, projected_point, MathTex("Z_1").next_to(rect1_dot, UP), MathTex("Z_2").next_to(rect2_dot, UP), MathTex("-n").next_to(vert_line, UP))

        self.wait()
        self.play(Transform(rect1_dot, projected_point))
        self.wait()
        self.play(Transform(rect2_dot, projected_point))
        self.wait()
