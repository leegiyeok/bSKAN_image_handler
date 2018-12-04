# Made by Giyeok Lee (2018.11.21)
# Here, Like c2c.py, setting gridpoints in jobfile is better, I think.
# How to set Isosurface?
# Input file : CURSAVE

import os, shutil, glob
import math
import sys
import time
import argparse
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
## for colormap. if you use only 'hot' and 'gray' cmap, it's no in need. -> cmap=hot also can be used in cmap=cm.hot
#from matplotlib import cm
import matplotlib.pyplot as plt
from scipy import interpolate

s_t=time.time()
resu=open("[plot] GEN_REPORT.txt",'a')
if os.path.isfile('[plot] real_xy_position.txt'):
    df=open('[plot] real_xy_position.txt','w')
    df.close()
if os.path.exists("CURSAVE"):

	pars = argparse.ArgumentParser()
	pars.add_argument('X', type = int, help='x grids')
	pars.add_argument('Y', type = int, help='y grids')
	pars.add_argument('Z', type = int, help='z grids')
	pars.add_argument('-r', type = int, help='round digit', default=10)
	pars.add_argument('-cmap', type=str, help='hot, gray')
	args  = pars.parse_args()
	nx, ny, nz, rdigit, cmap = args.X, args.Y, args.Z, args.r, args.cmap


	f = open("CURSAVE", 'r')
	fft_total = int(nx) * int(ny) * int(nz)
	t_len=fft_total+int(nx)*int(ny)
	sall = f.readlines()
	f.close()

	try:
	    [float(x) for x in sall[0].rstrip("\n").split(" ") if x!=""]
	    
	except:
	    sall=sall[1:]


	if len(sall)>=t_len and len(sall)<=t_len+2:
	    print("[good] (%s,%s,%s) is valid grid point numbers."%(nx,ny,nz), file=resu)
	    xyz_gridver=dict()
	    z_fromxy=dict()
	    # extract data from CURSAVE
	    for iz in range(0,nz+1):
	        for iy in range(1,ny+1):
	            for ix in range(1,nx+1):
	                temp=((ix-1)*ny+(iy-1))*(nz+1)+iz
	                a=sall[temp]

	                if iz!=0:
	                    val=float(sall[temp].rstrip('\n'))
	                    # I take rounding method, but I think +- specific value is also possible
	                    val=round(val,rdigit)
	                    if not(val in xyz_gridver):
	                        xyz_gridver[val]=dict()
	                  # I will take higher value when overlapped. But I want to get similar values comparing with neighbor values.
	                    if (ix, iy) in xyz_gridver[val]:
	                        xyz_gridver[val][(ix, iy)]=max(xyz_gridver[val][(ix, iy)],iz)                   
	                    else:
	                        xyz_gridver[val][(ix, iy)]=iz
	  
	                  # when iz=0
	                else:
	                    xy_l=[float(x) for x in a.rstrip('\n').split(" ") if x!=""]
	                    xy=open('[plot] real_xy_position.txt','a')
	                    print("%f   %f"%(xy_l[0], xy_l[1]), file=xy)
	        xy.close()
	else:
	    print("[error] (%s,%s,%s) is wrong grid point numbers."%(nx,ny,nz), file=resu)
	resu.close()

	TiMe=open('[plot] time.txt','w')
	print("---%s seconds ---"%(time.time()-s_t),file=TiMe)
	TiMe.close()


	iso_list=list(xyz_gridver)
	avail_iso_list=[x for x in iso_list if len(xyz_gridver[x])>=nx*ny]
	X,Y=np.arange(1,nx+1,1), np.arange(1,ny+1,1)
	X,Y=np.meshgrid(X,Y)
	Z=np.zeros((ny,nx))
	for i in range(0,nx):
	    for p in range(0,ny):
	        Z[p,i]=xyz_gridver[avail_iso_list[0]][(i+1,p+1)]

	fig = plt.figure(figsize=(12,12))
	ax = fig.gca(projection='3d')
	# best recommended : afmhot, hot, gray
	# second recommended : gist_heat, autumn
	# Visit https://matplotlib.org/users/colormaps.html to get more information about selecting cmaps
	# ax.plot_surface(X, Y, grid ,cmap='hot', rstride=1, cstride=1, edgecolor='none', linewidth=0.1)
	ax.plot_surface(X, Y, Z ,cmap=cmap, rstride=1, cstride=1, edgecolor='none', linewidth=0)
	#view_init(x,y) : set view direction(elevation and azimuthal angles). (90,0) means 90 degrees above the x-y plane(perpendicular) and an azimuth of 0 degree(rotated 0 degree counter-clockwise about the z-axis).
	ax.view_init(90,0)

	plt.savefig('testing.png')


else:
	print("[plot] There is no CURSAVE file",file=resu)