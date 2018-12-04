from PIL import Image
from math import pi, sin, cos
import os
import argparse

pars = argparse.ArgumentParser()
pars.add_argument('-gamma', type=float, default=90.0, help="gamma value")
pars.add_argument('x', type=int, default=4, help="horizontal iteration")
pars.add_argument('y', type=int, default=3, help="vertical iteration")
args=pars.parse_args()
gamma=args.gamma
x=args.x
y=args.y

def image_iter(file, x, y, gamma, name="iterated_image"):
    im = Image.open(file)
    size_x, size_y = im.size
    G=gamma*pi/180
    s_g, c_g = sin(G), cos(G)

    # when gamma=90, x_cut=0
    x_cut = int(round(size_y*c_g/s_g,0))

    directory = os.path.dirname("generated_iter/")
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    new_image = Image.new("RGBA", (size_x * x, size_y * y), (255, 255, 255, 0))
#     for ix in range(x):
#         for iy in range(y):
#             new_image.paste(imi, (size_x * ix, size_y * iy, size_x * (ix + 1), size_y * (iy + 1)))
#     new_image.save("generated_png/" + name + "_%sx%s" % (x, y) + ".png", "PNG")

    if x_cut==0:
        for ix in range(x):
            for iy in range(y):
                new_image.paste(im, (size_x * ix, size_y * iy, size_x * (ix + 1), size_y * (iy + 1)))
    else:
        for iy in range(y):
            ix_cut = (iy*x_cut) % size_x
            im_left  = im.crop(((ix_cut, 0, size_x, size_y)))
            im_right = im.crop(((0, 0, ix_cut, size_y)))
            new_image.paste(im_left, (0, size_y * iy, size_x-ix_cut, size_y * (iy+1)))
            new_image.paste(im_right, (size_x*x-ix_cut, size_y*iy, size_x*x, size_y * (iy+1)))
            for ix in range(x-1):
                new_image.paste(im, ((size_x-ix_cut)+size_x*ix, size_y*iy, (size_x-ix_cut)+size_x*(ix+1), size_y*(iy+1)))
    new_image.save("generated_iter/" + name + "_%sx%s" % (x, y) + ".png", "PNG")

image_iter('44_structure_STM.png',x,y,gamma,name)





