---
title: 'Perspective Projection Matrix'
date: 2024-09-01T08:26:12+01:00
draft: false
math: true
cover:
    image: "perspective_matrix/1.png"
---

I usually find it hard to take something at face value, while doing some graphics programming,
I frequently came across matrices, and for the most part, they were not that complex since I knew
some linear algebra beforehand. However, the perspective projection matrix seemed confusing, and I
couldn't wrap my head around it, so I decided to reconstruct it from the ground up

##### Intuition
Well, we have a 3D scene, but our screen is 2D. we need to somehow draw 3D on a 2D surface, so
we need some kind of mapping

![](/perspective_matrix/1.gif)

#### Diving Deep
so let's think of one point

![](/perspective_matrix/2.gif)

as you can see, it's kind of hard to work with it like this, so let's look at it from the side and the top

![](/perspective_matrix/8.png)
![](/perspective_matrix/9.png)

what we need to do is figure out where it's going to land on that blue plane/near_plane

![](/perspective_matrix/10.png)

$$
\frac{y_p}{y} = -\frac{n}{z}
$$
$$
y_p = -\frac{n * y}{z}
$$


since we want all the points to be projected into [-1, 1] in all dimension, i just put the height to
be 1, later we will deal with values different than [-1, 1]

### {{<colored "cyan" >}} Note: {{</colored>}}
- n: how far near plane from the camera (-n) just because I intend to pass positive values

![](/perspective_matrix/11.png)

$$
\frac{x_p}{x} = -\frac{n}{z}
$$
$$
x_p = \frac{-n * x}{z}
$$

let's look at some numbers to get a more intuitive feeling

![](/perspective_matrix/12.png)


$$
x_p = \frac{-n * x}{z}
$$

$$
x_p = \frac{-4 * (-4)}{-8} = -2
$$


$$
y_p = \frac{-n * y}{z}
$$

$$
y_p = \frac{-4 * 2}{-8} = 1
$$

and  z will be same as n so $$ z = -n = -4 $$

$$
\vec{v} = \begin{bmatrix} -2 \\\ 1 \\\ -4 \end{bmatrix}
$$

![](/perspective_matrix/3.gif)

now we need to develop matrix that do this transformation, what transformation?
well just scaling x and y by
$$-\frac{n}{z}$$
since a lot of people use fov (filed of view) a lot I'll use it also

![](/perspective_matrix/13.png)



$$
tan(\frac{fov}{2}) = \frac{1}{n}
$$
$$
n = \frac{1}{tan(\frac{fov}{2})}
$$

so now I need to scale x and y by

$$
\frac{1}{-tan(\frac{fov}{2}) * z}
$$

But how would you scale something like this? If it were just a number, it would be easy—just something like this

$$
\begin{bmatrix}
s1 & .. & .. & 0 \\\
.. & s2 & .. & 0 \\\
.. & .. & s3 & 0 \\\
.. & .. & .. & 1
\end{bmatrix} 
$$

bBut in our case, we have a z-component involved, which is not ideal because I want a general matrix, not one that is specific to each vertex. However, there’s a way—something called perspective divide. This means that the rasterizer in OpenGL will divide by w. But what is w, you ask? It’s just the fourth component of the vector/position.
$$\vec{v} = \begin{bmatrix} x, \\ y, \\ z, \\ w \end{bmatrix}$$
so the idea is that I don't need to scale by

$$
\frac{1}{-tan(\frac{fov}{2}) * z}
$$

i could remove the *z*

$$
\frac{1}{-tan(\frac{fov}{2})}
$$

Change the matrix so that it places z in place of w. During the perspective divide, the rasterizer will divide by w, which is now z, and then we get the correct result.
$$x_p$$

So, here’s the matrix that will copy z to the final w.

$$
\begin{bmatrix}
.. & .. & .. & 0 \\\
.. & .. & .. & 0 \\\
.. & .. & .. & 0 \\\
.. & .. & 1 & ..
\end{bmatrix} 
\begin{bmatrix}
x \\\
y \\\
z \\\
1
\end{bmatrix} = 
\begin{bmatrix}
.. \\\ .. \\\ .. \\\ z
\end{bmatrix} 
$$

So, when the rasterizer gets this
$$
\begin{bmatrix}
.. \\\ .. \\\ .. \\\ z
\end{bmatrix} 
$$

It will divide by w—oops, I meant to say z—so we get the correct scale. Now, let’s add the 
scaling matrix.
$$
\begin{bmatrix}
\frac{1}{-tan(\frac{fov}{2})} & .. & .. & 0 \\\
.. & \frac{1}{-tan(\frac{fov}{2})} & .. & 0 \\\
.. & .. & .. & 0 \\\
.. & .. & 1 & ..
\end{bmatrix} 
$$

since there's no translation
$$
\begin{bmatrix}
\frac{1}{-tan(\frac{fov}{2})} & 0 & 0 & 0 \\\
0 & \frac{1}{-tan(\frac{fov}{2})} & 0 & 0 \\\
.. & .. & .. & 0 \\\
.. & .. & 1 & ..
\end{bmatrix} 
$$

Since there's that common '-' sign, let's use it with z, so we are dividing by -z. We just 
need to change the part that is responsible for copying z to w.
$$
\begin{bmatrix}
\frac{1}{tan(\frac{fov}{2})} & 0 & 0 & 0 \\\
0 & \frac{1}{tan(\frac{fov}{2})} & 0 & 0 \\\
.. & .. & .. & 0 \\\
.. & .. & -1 & ..
\end{bmatrix}
$$

### {{<colored "RED" >}} NOTE: {{</colored>}}
- don't worry about z value for now

now let's address the elephant in the room **Aspect Ratio**
what does that mean? well since usually width is greater than the height stuff
is going to be stretched in the x-axis let's see example 

![](/perspective_matrix/14.png)

![](/perspective_matrix/4.gif)

![](/perspective_matrix/15.png)

![](/perspective_matrix/5.gif)

As you can see, the scaling is messed up—the final picture is not what we intended. I was expecting to see the square (the front face of our cube), but we can solve this by scaling down the x-axis to match our needs. Since the width is twice the height, it means that for every pixel in height, there are two corresponding pixels in width. Therefore, we need to scale down the width by a factor of 2 so that the final result matches.

![](/perspective_matrix/6.gif)

Now it looks good. You may notice that we could also scale the height by a factor of 2 to 
achieve the correct result.

![](/perspective_matrix/7.gif)
Yes, the ratio is correct, but if we have NDC coordinates with a height ranging from -1 to 1, we would be outside this range. Therefore, I prefer to scale down, but experimenting can help you get a more intuitive idea.

### {{< colored "green" >}} result {{</colored>}}
scale down by the aspect ratio
$$
ratio = ar = \frac{width}{height}
$$

so here's how the matrix now should look like

$$
\begin{bmatrix}
\frac{1}{tan(\frac{fov}{2}) * \bold{\color{green}{ar}}} & 0 & 0 & 0 \\\
0 & \frac{1}{tan(\frac{fov}{2})} & 0 & 0 \\\
.. & .. & .. & 0 \\\
.. & .. & -1 & ..
\end{bmatrix}
$$

now we are going to need to deal with z stuff but why isn't every point lines on -n?

![](/perspective_matrix/8.gif)

As you can see, if we change every z value to -n, the rasterizer won't be able to 
differentiate between vertices when it gets them. Specifically, it won't know which one 
should be rendered because the closer one should be rendered, but by replacing z values with 
-n, we lose that information. That’s why I mentioned before not to worry about z values. We 
could simply choose not to change the z value, and that would solve the issue.

$$
\\left[\\begin{matrix}\\frac{1}{ar * \\tan{\\left(\\frac{fov}{2} \\right)}} & 0 & 0 & 0\\\\0 & \\frac{1}{\\tan{\\left(\\frac{fov}{2} \\right)}} & 0 & 0\\\\0 & 0 & 1 & 0\\\\0 & 0 & -1 & 0\\end{matrix}\\right] *
\\left[\\begin{matrix}x\\\\y\\\\z\\\\1\\end{matrix}\\right]
= \\left[\\begin{matrix}\\frac{n x}{ar * \\tan{\\left(\\frac{fov}{2} \\right)}}\\\\\\frac{n y}{\\tan{\\left(\\frac{fov}{2} \\right)}}\\\\\bold{\color{BLUE}{z}}\\\\- z\\end{matrix}\\right]
$$

Is that it? Well, not quite. There’s also something called z-fighting, which I won't go into 
detail about here. However, z will also be mapped to the range of -1 to 1.

$$
\\left[\\begin{matrix}\\frac{1}{ar * \\tan{\\left(\\frac{fov}{2} \\right)}} & 0 & 0 & 0\\\\0 & \\frac{1}{\\tan{\\left(\\frac{fov}{2} \\right)}} & 0 & 0\\\\0 & 0 & A & B\\\\0 & 0 & -1 & 0\\end{matrix}\\right]*
\\left[\\begin{matrix}x\\\\y\\\\z\\\\1\\end{matrix}\\right] = 
\\left[\\begin{matrix}\\frac{n x}{ar * \\tan{\\left(\\frac{fov}{2} \\right)}}\\\\\\frac{n y}{\\tan{\\left(\\frac{fov}{2} \\right)}}\\\\\bold{\color{GREEN}{A z + B}}\\\\- z\\end{matrix}\\right]
$$

why don't I fill the other zeros (C/D)

$$
\\left[\\begin{matrix}\\frac{1}{ar * \\tan{\\left(\\frac{fov}{2} \\right)}} & 0 & 0 & 0\\\\0 & \\frac{1}{\\tan{\\left(\\frac{fov}{2} \\right)}} & 0 & 0\\\\C & D & A & B\\\\0 & 0 & -1 & 0\\end{matrix}\\right]
$$

well because z has nothing to do with x and y

we know that rasterizer will divide every component include z so the final point will look
something like this
$$
Z_p = \frac{A z + B}{w=-z}
$$

$$
Z_p = A + \frac{B}{-z}
$$

so we just need to find A and B and fill the reset of the matrix, we have

$$
-1 = A + \frac{B}{-(-n)} = A + \frac{B}{n}
$$

$$
1 = A + \frac{B}{-(-f)} = A + \frac{B}{f}
$$

what is f? well it stands for near plane just like *n* just far plane

after some gymnastics

$$
A = -\frac{f + n}{f - n}
$$

$$
B = -\frac{2 *f n}{f - n}
$$

so this is the resulting matrix

$$
\\left[\\begin{matrix}\\frac{1}{ar * \\tan{\\left(\\frac{fov}{2} \\right)}} & 0 & 0 & 0\\\\0 & \\frac{1}{\\tan{\\left(\\frac{fov}{2} \\right)}} & 0 & 0\\\\0 & 0 & -\\frac{f + n}{f - n} & - \\frac{2 f n}{f - n}\\\\0 & 0 & -1 & 0\\end{matrix}\\right]
$$