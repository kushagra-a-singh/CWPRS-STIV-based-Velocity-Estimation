# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 18:41:28 2015
@author: sp
Reads DXF file created by the disto, and plots the markers
Data from the disto:
- 2DG --> this is the floor plan (view from the top)
- 2DW --> this is the front view. This file will only be created if between
  first and second measurement the horizontal movement was at least 10cm.
  Otherwise no horizontal axis can be defined for presentation.
- 3D --> this is the 3D drawing
The first measured point is the reference for the drawing.
The second point defines the x-axis.
The y-axis and z-axis are rectangular to it also referenced to the
horizontal plane (levelling).
An exception to this would be if the horizontal distance between
the first and second measured point is less than 10cm. In such case the DISTO
will be the reference in the drawing and the direction to the first measured
point will be the x-axis.
Dist Z values are moved so there are no negative values
If a "profile_offset.txt" file exists the Disto Z values will be further moved
up by that amount.
"""


import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os
import sys
import numpy as np
path = r"./"

##############################################################################
# - Disto file: -
disto_file = './sample_3D.dxf'

# - profile offset -
offset_file = path + './profile_offset.txt'
##############################################################################


disto_file_exists = os.path.isfile(disto_file)
if not disto_file_exists:
    sys.exit("File -disto.dxf- does not exist")

offset = False
offset_file_exists = os.path.isfile(offset_file)
if offset_file_exists:
    offset_val = np.loadtxt(offset_file)
    offset = True

# --- read dxf file and get coordinates ---
# -get indicators where points are located -
count = 0
ind_points = []
with open(disto_file, 'r') as f:
    for line in f:
        count = count + 1
        if "AcDbPoint" in line:
            a = line
            ind_points.append(count)

x = []
y = []
z = []
for p in range(0, len(ind_points)):
    fp = open(disto_file)
    for i, line in enumerate(fp):
        if i == ind_points[p] + 1:
            x.append(float(line))
        if i == ind_points[p] + 3:
            y.append(float(line))
        if i == ind_points[p] + 5:
            z.append(float(line))
    fp.close()
print ("Disto file read")


# - Move min Z to 0 -
z_array = np.asanyarray(z)
z_min = z_array.min()
for i in range(len(z)):
    #BEAT z[i] = z[i] - z_min
    if offset:
        z[i] = z[i] + offset_val
#Beat print "Disto Z values are positive now"


# - Move min Y to 0 -
y_array = np.asanyarray(y)
y_min = y_array.min()
#BEAT for i in range(len(y)):
    #BEAT y[i] = y[i] - y_min
#BEAT print "Disto Y values are positive now"


# - Move min X to 0 -
x_array = np.asanyarray(x)
x_min = x_array.min()
#BEAT for i in range(len(x)):
    #BEAT x[i] = x[i] - x_min
#BEAT print "Disto Y values are positive now"


# - save makers coordinates into txt file -
output_file = path + '/disto.txt'
with open(output_file, "w") as myfile:
    for num in range(len(x)):
        myfile.write(str(x[num]) + '\t' + str(y[num]) + '\t' + str(z[num]))
        myfile.write('\n')
print ("disto.txt created")


# - plot -
fig = plt.figure('3D view', figsize=(15, 5))
plt3d = fig.add_subplot(111, projection='3d')
for i in range(len(x)):
    plt3d.scatter(x[i], y[i], z[i], color='b')
    plt3d.text(x[i], y[i], z[i], '%s' % (str(i+1)), size=14, zorder=1,
               color='k')
plt3d.set_xlabel("X (m)")
plt3d.set_ylabel("Y (m)")
plt3d.set_zlabel("Z (m)")
plt3d.set_title(disto_file)
# plt3d.axis('equal')
plt.show()