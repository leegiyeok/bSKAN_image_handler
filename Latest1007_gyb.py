# remove black edge of tiff image(simulated stm image from openDX) and make images(png : no black edge) iterated and blurring
# Giyeok Lee, 2018_08_21
# Modified by Giyeok Lee, 2018_10_07 (Using argparse)
# If you don't have any packages, 'pip3 install --user scipy matplotlib argparse Pillow' will install all packages which this python script wants.
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import os
import glob
# You can install PIL package by 'pip install --user Pillow' or 'python3 -m pip install --user Pillow'
from PIL import Image
import argparse



# -------------------------------------------------------------------------------- [input]
pars = argparse.ArgumentParser()
pars.add_argument('-n', type = int,nargs=2,default=[4, 2], help='number of iteration. nx ny')
pars.add_argument('-m', type = int, help='Which task do you want. 1=Do all tasks, 2=iteration+blur, 3=only remove black edge, 4=only iterating, 5=only blur',default=1)
pars.add_argument('-bm',type=int,help='blur mode. (how to select blur sigma) 1:single blur sigma value(bsv), 2:range of blur sigma value(bsl)',choices=[1,2], default=1)
pars.add_argument('-bsv',type=str,default='20',help='single blur sigma value (when you choose blur mode=1)')
pars.add_argument('-bsl',type=str,nargs=2,default=['20', '25'],help="range of blur sigma value. (when you choose blur mode=2)")
pars.add_argument('-ext',type=str,default='tiff',help="format of input images (ex. png, tiff, jpg)")
args = pars.parse_args()

mode, blur_mode, blur_sigma, blur_sigma_r, ext = args.m, args.bm, args.bsv, args.bsl, args.ext
if blur_mode==2:
    blur_sigma=" ".join(blur_sigma_r)
x,y=int(args.n[0]),int(args.n[1])


files=glob.glob("*."+ext)
print("Run for %s file(s)."%(len(files)))


# -------------------------------------------------------------------------------- [remove black edge] -> generate png and save pngin rm_blackbox/ directory

def rm_blackbox(file,name="cut_image"):
    im=Image.open(file)
    size_x,size_y=im.size
    directory = os.path.dirname("rm_blackbox/")
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    pix=im.load()
    
    def blackbox_check(a,b):
        while True:
            if pix[a,b]==(0,0,0):
                break
            else:
                if a==size_x-1:
                    a=0; b+=1
                else:
                    a+=1

        #find the x size of black edge box
        for i in range(1,int(size_x/2)):
            h_a=size_x-i
            if pix[h_a,b]==(0,0,0):
                break
        #find the y size of black edge box
        for p in range(1,int(size_y/2)):
            v_b=size_y-p
            if pix[a,v_b]==(0,0,0):
                break

        # box test
        if pix[h_a,v_b]==(0,0,0):
            return (a,b,h_a,v_b,"ok")
        else:
            return (a,b,h_a,v_b,"fail")

    (a,b,h_a,v_b,c)=blackbox_check(0,0)

    if c=="ok":
        #im.crop((left,upper,right,lower))
        img2=im.crop(((a+1,b+1,h_a,v_b)))
        img2.save("rm_blackbox/"+name+".png","PNG")
    else:
        print("rm_blackbox failed in \"%s\". Can't find black edge."%(file))
    
# -------------------------------------------------------------------------------- [image iterating] -> generate png and save it to generated_png/ directory
def image_iter(file,x,y,name="iterated_image"):
    imi=Image.open(file)
    size_x,size_y=imi.size
    
    new_image=Image.new("RGB",(size_x*x,size_y*y),(255,255,255))
    directory = os.path.dirname("generated_png/")
    if not os.path.exists(directory):
        os.makedirs(directory)
    for i in range(x):
        for p in range(y):
            new_image.paste(imi,(size_x*i,size_y*p,size_x*(i+1),size_y*(p+1)))
    new_image.save("generated_png/"+name+"_%sx%s"%(x,y)+".png","PNG")
    # save(self, filename, format=None, **param) -> format dafault=input image file format (if possible)


# --------------------------------------------------------------------------------  [blurring] -> generate png and save it to generated_blur/ directory
def image_blur(file,blur_sigma,name="blurred_image"):
    '''blur_sigma = blur strength, only blur task -> onlyblur='t' '''
    imgb=plt.imread(file)

    directory = os.path.dirname("generated_blur/")
    if not os.path.exists(directory):
        os.makedirs(directory)

    if len(blur_sigma.split(" "))==1:
        # Note the 0 sigma for the last axis, we don't wan't to blurr the color planes together
        # sigma : scalar or sequence of scalars. Standard deviation for Gaussian kernel.
        #         The standard deviations of the Gaussian filter are given for each axis as a sequence,
        #         or as a single number, in which case it is equal for all axes.
        blur_sigma=int(blur_sigma)
        imgb2 = ndimage.gaussian_filter(imgb, sigma=(blur_sigma, blur_sigma, 0), order=0)
        plt.imshow(imgb2, interpolation='nearest')
        plt.imsave("generated_blur/"+name+'_sigma=%s.png'%(blur_sigma),imgb2)

    else:
        for i in range(int(blur_sigma.split(" ")[0]),int(blur_sigma.split(" ")[1])+1):
            imgb2 = ndimage.gaussian_filter(imgb, sigma=(i, i, 0), order=0)
            plt.imshow(imgb2, interpolation='nearest')

            directory = os.path.dirname("generated_blur/"+name+"/")
            if not os.path.exists(directory):
                os.makedirs(directory)

            plt.imsave("generated_blur/"+name+"/"+name+'_sigma=%s.png'%(i),imgb2)


    



# -------------------------------------------------------------------------------- [operate] : run functions for all files in current directory


for file in files:
    name=file.rstrip(ext).rstrip(".")
    
    
    # mode 1 = remove black edge(box) + Image iteration + Image blurring
    if mode==1:
        rm_blackbox(file, name)
        try:
            image_iter("rm_blackbox/"+name+".png", x, y, name)
        except FileNotFoundError as e:
            print(e)
            image_iter(file, x, y, name)
        try:
            image_blur("generated_png/"+name+"_%sx%s"%(x,y)+".png", blur_sigma, name)
        except FileNotFoundError as e:
            print(e)
            image_blur(file,blur_sigma, name)

    # mode 2 = Image Iteration + Image blurring
    elif mode==2:
        try:
            image_iter(file, x, y, name)
            image_blur("generated_png/"+name+"_%sx%s"%(x,y)+".png", blur_sigma, name)
        except FileNotFoundError as e:
            print(e)
            image_blur(file,blur_sigma, name)
    # mode 3 = only black edge(box) cutting
    elif mode==3:
        rm_blackbox(file, name)
    # mode 4 = only image iterating
    elif mode==4:
        image_iter(file, x, y, name)
    
    # mode 5 = only blur
    elif mode==5:
        image_blur(file, blur_sigma, name)
        
    # mode input error
    else:
        print("mode input error. Please input 1~5 integer")

    # exist just because english ordinal
    if files.index(file)+1 in [1,2,3]:
        ind=['st','nd','rd'][files.index(file)]
    else:
        ind='th'
    print("%2s%s file done among %s files" %(files.index(file)+1,ind,len(files)))
print("job's done")
