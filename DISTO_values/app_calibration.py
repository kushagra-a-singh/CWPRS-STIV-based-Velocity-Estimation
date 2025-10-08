"""
author: Thomas Philippe
compagny: Photrack AG
email: philippe@photrack.ch

Helper script to transform topographic data from the field
to proper format used in www.discharge.ch for free or natural cross-sections.

Needs the following files:
1. cross_section.txt: can be n lines (min: n=3), 3 columns (x,y,z coordinates)
   The file describes the cross sectional profile.
2. cross_section_offset.txt (optional): This file contains a single value, the lenght
   of the stick used to measured the cross section
3. markers.txt: must have 4 lines and 3 columns, contains the x,y,z
   coordinates of the markers 1 (far left), 2 (far right), 3 (close left),
   4 (close right):
4. shoreline.txt: at least 2 points of the far water shorline.
   2-n lines, 3 columns, x,y,z coordinate of water shorline.
   The shorline defines the x-direction, i.e. the vector pointing downstream
   and parallel to the water surface
"""

import argparse
import json
import os
import sys
import qrcode

import numpy as np
import scipy.optimize

import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d.axes3d import get_test_data
# from matplotlib import cm
# from matplotlib.ticker import LinearLocator, FormatStrFormatter
# from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# import pylab as pl
# from pprint import pprint
# import matplotlib
# matplotlib.use('GTKAgg')

# sys.setrecursionlimit(10000)


def exitError(msg):
    print("An error occurs:", msg)
    sys.exit()


def getRotationMatrix(axis, angle):
    """
    Rotation matrix from axis and angle
    """
    axis /= np.linalg.norm(axis)
    c = np.cos(angle)
    s = np.sin(angle)
    R = np.zeros((3, 3))
    R[0, 0] = axis[0] * axis[0] * (1-c) + c
    R[0, 1] = axis[0] * axis[1] * (1-c) - s*axis[2]
    R[0, 2] = axis[0] * axis[2] * (1-c) + s*axis[1]

    R[1, 0] = axis[0] * axis[1] * (1-c) + s*axis[2]
    R[1, 1] = axis[1] * axis[1] * (1-c) + c
    R[1, 2] = axis[1] * axis[2] * (1-c) - s*axis[0]

    R[2, 0] = axis[0] * axis[2] * (1-c) - s*axis[1]
    R[2, 1] = axis[1] * axis[2] * (1-c) + s*axis[0]
    R[2, 2] = axis[2] * axis[2] * (1-c) + c

    return R


def getRotation2X(p0, d):
    """
    :p0:
    :d:
    :n: axis to apply rotation
    :angle: angle to rotate around axis
    """
    # get normal vector to plane between x and d
    x = np.array((1, 0, 0))
    n = np.cross(x, d)
    if np.linalg.norm(n) == 0:
        return np.diag(np.ones(3))
    n /= np.linalg.norm(n)

    # get angle between x and d:
    angle = np.dot(x, d)
    angle /= np.linalg.norm(d)
    angle = np.arccos(angle)
    # construct rotation matrix
    return getRotationMatrix(n, -angle)


def objectiveFunc(vals, points):
    x0 = np.zeros(3)
    x0 = vals[0:3]
    d = vals[3:6]
    d /= np.linalg.norm(d)
    sum = 0
    for pt in points.T:
        v = pt-x0
        v = np.dot(v, d) * d - v
        sum += np.linalg.norm(v)

    return sum


def fit3dLine(pts):
    vals = np.zeros(6)
    vals[0: 3] = pts[:, 0]  # (x y z) first point
    vals[3: 6] = pts[:, 1] - pts[:, 0]  # (x y z) second point - first point
    result = scipy.optimize.minimize(objectiveFunc, vals, args=(pts,),
                                     method='Nelder-Mead',
                                     options={'disp': False, 'maxiter': 1e4,
                                              'xtol': 1e-10, 'return_all': False,
                                              'ftol': 1e-10, 'maxfev': 1e4})
    result = scipy.optimize.minimize(objectiveFunc, result.x, args=(pts,),
                                     method='Nelder-Mead',
                                     options={'disp': False, 'maxiter': 1e4,
                                              'xtol': 1e-11, 'return_all': False,
                                              'ftol': 1e-11, 'maxfev': 1e4})
    x0 = result.x[0: 3]
    d = result.x[3: 6]
    d /= np.linalg.norm(d)

    return (x0, d)


def fillCoordinatesData(jdata, field):
    d = jdata[field]
    coords = np.zeros((3, len(d['x'])))
    coords[0][:] = np.array(d['x'])
    coords[1][:] = np.array(d['y'])
    coords[2][:] = np.array(d['z'])

    return coords


def write_data(filenameprefix, riveraxis, mcoords, profile):
    json_data = {}
    json_data["shoreline"] = {}
    json_data["markers_world_coordinates"] = {}
    json_data["profile"] = {}

    json_data["shoreline"]["x"] = riveraxis[0, :].tolist()
    json_data["shoreline"]["y"] = riveraxis[1, :].tolist()
    json_data["shoreline"]["z"] = riveraxis[2, :].tolist()

    mcoords = np.round(mcoords,3)
    profile = np.round(profile,3)

    json_data["markers_world_coordinates"]["x"] = mcoords[0, :].tolist()
    json_data["markers_world_coordinates"]["y"] = mcoords[1, :].tolist()
    json_data["markers_world_coordinates"]["z"] = mcoords[2, :].tolist()

    json_data["profile"]["x"] = profile[0, :].tolist()
    json_data["profile"]["y"] = profile[1, :].tolist()
    json_data["profile"]["z"] = profile[2, :].tolist()
    print("Writing parameters to", filenameprefix)
    with open(filenameprefix+".json", 'w') as outfile:
        json.dump(json_data, outfile, sort_keys=True,
                  indent=4, ensure_ascii=False)
    np.savetxt(filenameprefix+"_GCPs.txt",
               mcoords.flatten().reshape((1, mcoords.size)),
               delimiter=',', fmt='%1.4f')
    np.savetxt(filenameprefix+"_cross_section.txt",
               profile[1:3, :].flatten().reshape((1, profile[1:3, :].size)),
               delimiter=',', fmt='%1.4f')
               
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=5,
                       border=5)
    
    # QR code generation
    free_params = profile[1,:].tolist()   
    free_params.extend(profile[2,:].tolist())    
    
    markers_coordinates = mcoords[0, :].tolist()
    markers_coordinates.extend(mcoords[1, :].tolist())
    markers_coordinates.extend(mcoords[2, :].tolist())    
    
    qr_free = {}
    qr_free["free_params"] = free_params
    qr_markers = {}
    qr_markers["markers_coordinates"] = markers_coordinates
#    qr_data["free_params"] = json_data["profile"]["x"].extend(json_data['profile']['y'].extend(json_data['profile']['z']))
#    qr_data['profile'] = profile.tolist()
#    qr_data['mcoords'] = mcoords.tolist()
#    qr_data = [profile.tolist(), mcoords.tolist()]
#    qr.add_data(qr_data)
    
    qr.add_data(json.dumps(qr_free))
    qr.make(fit = True)
    img = qr.make_image()
    img.save(filenameprefix + '_qr_cross_section.png')

    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=5,
                       border=5)

    qr.add_data(json.dumps(qr_markers))
    qr.make(fit = True)
    img = qr.make_image()
    img.save(filenameprefix + '_qr_GCPs.png')

def find_wlevel_onprofile(profile, hw, reverse=False):
    if reverse:
        profile = np.fliplr(profile)
    # y = profile[1, :]
    zfrombed = profile[2, :]-profile[2, :].min()
    if zfrombed.max() < hw:
        exitError("Watercolumn should be consistent with the given profile.")
    idx = 0
    idxbefore = 0
    for i in range(zfrombed.size):
        if zfrombed[i] < hw:
            idx = i
            break
    if idx > 0:
        idxbefore = idx - 1

    tmp1 = profile[1, idxbefore] - profile[1, idx]
    tmp2 = profile[2, idxbefore] - profile[2, idx]
    slope = tmp1 / tmp2

    ypos = (hw-zfrombed[idx]) * slope + profile[1, idx]
    zpos = hw + profile[2, :].min()

    return np.array((profile[0, 0], ypos, zpos))


def apply_transformations(data, fig=None):
    # check if 2d profile:
    has2dprofile = False
    haswatercolumn = False
    profileoffset = 0
    if data['profile_offset'] is not None:
        profileoffset = data['profile_offset']

    if len(data['profile']['x']) == 0:
        data['profile']['x'] = [data['markers_world_coordinates']['x'][0] for i in range(len(data['profile']['y']))]
        has2dprofile = True

    data['profile']['z'] = [data['profile']['z'][i] - profileoffset for i in range(len(data['profile']['z']))]

    shoreline = fillCoordinatesData(data, 'shoreline')
    markers_worldcoordinates = fillCoordinatesData(data,
                                                   'markers_world_coordinates')
    profile = fillCoordinatesData(data, 'profile')
    if data['watercolumn'] is not None:
        hw = data['watercolumn']
        haswatercolumn = True

    if has2dprofile and not haswatercolumn:
        exitError("You need to specify watercolumn when using a 2d profile.")

    # - Check for four markers -
    if markers_worldcoordinates.shape[1] == 4:
        # check if right-handed system of coordinates:
        v0 = markers_worldcoordinates[:, 0] - markers_worldcoordinates[:, 2]
        v1 = markers_worldcoordinates[:, 1] - markers_worldcoordinates[:, 2]
        v3 = markers_worldcoordinates[:, 3] - markers_worldcoordinates[:, 2]
        if not(np.cross(v3, v0)[2] > 0 and np.cross(v3, v1)[2] > 0 and np.cross(v1, v0)[ 2 ]>0):
            print("Left-handed system of coordinate. \
                  Transorming to right-handed system...")
            markers_worldcoordinates[0, :] *= -1.
            shoreline[0, :] *= -1.
            if has2dprofile:
                profile[0, :] *= -1.
    else:
        exitError("Need four markers for the calibration.")

    # - rotate points align up x axis along the river axis -
    (p0, d) = fit3dLine(shoreline)
    R = getRotation2X(p0, d)

    # print("markers_worldcoordinates before: ", markers_worldcoordinates)
    # print("shoreline before: ", shoreline)
    # print("profile before: ", profile)

    for i in range(markers_worldcoordinates.shape[1]):
        markers_worldcoordinates[:, i] = np.dot(R, markers_worldcoordinates[:, i])

    # shoreline_old = np.copy(shoreline)

    
    for i in range(shoreline.shape[1]):
        shoreline[:, i] = np.dot(R, shoreline[:, i])


    profile_old = np.copy(profile)

    """
    translation = np.zeros(3)
    translation[0] = markers_worldcoordinates[0, 0] #x translation
    translation[1] = 0 #y translation
    translation[2] = shoreline_old[2,0] - shoreline[2,0] if not haswatercolumn else 0#force shore z coordinates to remain the same.


    profile[0, :] = translation[0]
    """
    """ 2d profile and has watercolumn -> not same reference system:
            2d profile measured along gravity, so project profile on new z axis
            look where the shore line is on profile.
        3d column -> same refeference system
    """
    translation = np.zeros(3)
    if has2dprofile and haswatercolumn:
        # apply the shift if need be.
        # point coordinate on profile
        translation = find_wlevel_onprofile(profile, hw)
        translation -= shoreline[:, 0]
        kmin = np.argmin(profile[2, :])
        minpos = profile[:, kmin]

        # translate all the data to keep profile as reference:
        for i in range(markers_worldcoordinates.shape[1]):
            markers_worldcoordinates[:, i] += translation
        # check if we have taken the right shore:
        # it just checks if markers are outside the profile/don't surround the bed.
        if (markers_worldcoordinates[1,0] - minpos[1])*(markers_worldcoordinates[1,-1] - minpos[1])>0:
            for i in range(markers_worldcoordinates.shape[1]):
                markers_worldcoordinates[:, i] -= translation

            translation = find_wlevel_onprofile(profile, hw, reverse=True)
            translation -= shoreline[:, 0]
            for i in range(markers_worldcoordinates.shape[1]):
                markers_worldcoordinates[:, i] += translation

        for i in range(shoreline.shape[1]):
            shoreline[:, i] += translation
    else:

        for i in range(profile.shape[1]):
            profile[:, i] = np.dot(R, profile[:, i])

        kmin = np.argmin(profile_old[2, :])
        minpos = profile[:, kmin]

        translation[0] = -markers_worldcoordinates[0, 0]  # X
        translation[1] = -(profile[1, kmin] - profile_old[1, kmin])  # Y
        translation[2] = -(profile[2, kmin] - profile_old[2, kmin])

        for i in range(markers_worldcoordinates.shape[1]):
            markers_worldcoordinates[:, i] += translation

        for i in range(shoreline.shape[1]):
            shoreline[:, i] += translation

        for i in range(profile.shape[1]):
            profile[:, i] += translation

    # print("markers_worldcoordinates after: ", markers_worldcoordinates)
    # print("profile after: ", profile)
    # print("shoreline after: ", shoreline)

    # display end results:
    """
    fig, ax1 = plt.subplots()
    ax1.plot(profile[2,:], profile[1,:], 'b-')
    ax1.fill(profile[2,:], profile[1,:], 'b', alpha=0.3)
    ax1.set_ylabel('y [m]')
    # Make the y-axis label, ticks and tick labels match the line color.
    ax1.set_xlabel('z [m]', color='b')
    ax1.tick_params('x', colors='b')
    ax2 = ax1.twiny()
    ax2.plot(markers_worldcoordinates[0,:],
             markers_worldcoordinates[1,:], 'r*')
    ax2.set_xlabel('x [m]', color='r')
    ax2.tick_params('x', colors='r')
    fig.tight_layout()
    """

    if fig is None:
        fig = plt.figure(1)

    plt.subplot(211)
    plt.plot(profile[1, :], profile[2, :], '-b')
    plt.plot(shoreline[1, 0], shoreline[2, 0], '*g')
    plt.xlabel('y [m]')
    plt.ylabel('z [m]')
    plt.legend(["cross-section", "shoreline"])

    # plt.subplot(212)

    ax = fig.add_subplot(212, projection='3d')
    # ax = fig.gca(projection='3d')

    # plot markers
    ax.plot(markers_worldcoordinates[0, :],
            markers_worldcoordinates[1, :],
            markers_worldcoordinates[2, :], 'r*')

    # plot profile
    xmin = markers_worldcoordinates[0].min()
    xmax = markers_worldcoordinates[0].max()

    border = np.abs(xmin-xmax) * 0.05
    X = np.arange(xmin-border, xmax + 2*border, border)
    Y = profile[1, :]
    X, Y = np.meshgrid(X, Y)
    Z = np.matrix(profile[2, :]).transpose()
    Z = np.tile(Z, (1, X.shape[1]))

    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, alpha=0.3,
                    linewidth=0, antialiased=False)  #, cmap='binary')
    # cset = ax.contour(X, Y, Z, zdir='x')#, offset=markers_worldcoordinates[0,0]-2*border )
    # ax.plot(np.ones(profile.shape[1])*(markers_worldcoordinates[0,0]-3*border), profile[1,:], profile[2,:], 'b-')

    verts = []
    x = np.ones(profile.shape[1]) * (xmin - 6*border)
    y = profile[1, :]
    z = profile[2, :]

    # shift = np.array((0, profile[1, :].min(), profile[2, :].min()))

    verts = [list(zip(x, y, z))]
    poly = Poly3DCollection(verts)  # facecolor = ['b'])
    poly.set_alpha(0.7)
    ax.add_collection3d(poly)   # zs=markers_worldcoordinates[0,0]-3*border, zdir='x')

    # plot shoreline:
    (p0, d) = fit3dLine(shoreline)
    coeff = ((xmin-2 * border) - p0[0])/d[0]
    p1 = p0+coeff*d
    coeff = ((xmax + 2 * border) - p0[0])/d[0]
    p2 = p0+coeff*d
    
    ax.plot(np.array((p1[0], p2[0])),
            np.array((p1[1], p2[1])), np.array((p1[2], p2[2])), 'g-', linewidth=2)
    #ax.plot(np.array((xmin-2 * border, xmax + 2 * border)),
    #        np.array((p0[1], p0[1])), np.array((p0[2], p0[2])), 'g-', linewidth=2)
    ax.plot(shoreline[0,:], shoreline[1,:], shoreline[2,:], 'g*', linewidth=2)
    
    #ax.plot(np.array((xmin-2 * border, xmax + 2 * border)),
     #       shoreline[1, 0:2], shoreline[2, 0:2], 'g-', linewidth=2)

    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')

    ax.legend(['GCPs', 'shoreline fit', 'shoreline points'])

    plt.show()
    return (shoreline, markers_worldcoordinates, profile)


if __name__ == '__main__':
    currentpath = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", type=str, help=" Data file.")

    """
    parser.add_argument("-m", "--markers", type=str,
                        help=" Markers file.")
    parser.add_argument("-p", "--profile", type=str,
                        help=" Profile file.")
    parser.add_argument("-s", "--shoreline", type=str,
                        help=" Shoreline file.")
    parser.add_argument("-s", "--watercolumn", type=str,
                        help=" Watercolumn file.")
    """

    args = parser.parse_args()

    data = []
    data_file = ""
    markers_file = None
    profile_file = None
    shoreline_file = None
    watercolumn_file = None

    if args.data is not None:
        data_file = args.data
        print("Extracting parameters from", data_file, ".")
        with open(data_file) as file:
            data = json.load(file)
        data['watercolumn'] = None
    else:
        # data_file = 'data.json'
        data = dict()
        markers_file = 'GCPs.txt'
        profile_file = 'cross_section.txt'
        shoreline_file = 'shoreline.txt'
        watercolumn_file = 'watercolumn.txt'
        profileoffset_file = 'cross_section_offset.txt'
        if not os.path.isfile(markers_file):
            exitError("File "+markers_file+" doesn't exist!")
        if not os.path.isfile(profile_file):
            exitError("File "+profile_file+" doesn't exist!")
        if not os.path.isfile(shoreline_file):
            exitError("File "+shoreline_file+" doesn't exist!")

        data['shoreline'] = {}
        data['markers_world_coordinates'] = {}
        data['profile'] = {}
        mat = np.loadtxt(shoreline_file)
        # -  shore line has to be sorted from min X to max X -
        mat = mat[mat[:, 0].argsort()]
        mat = mat.transpose()
        data['shoreline']['x'] = mat[0][:].tolist()
        data['shoreline']['y'] = mat[1][:].tolist()
        data['shoreline']['z'] = mat[2][:].tolist()

        mat = np.loadtxt(markers_file)
        mat = mat.transpose()
        data['markers_world_coordinates']['x'] = mat[0][:].tolist()
        data['markers_world_coordinates']['y'] = mat[1][:].tolist()
        data['markers_world_coordinates']['z'] = mat[2][:].tolist()

        mat = np.loadtxt(profile_file)
        mat = mat.transpose()
        if mat.shape[0] == 2:
            data['profile']['x'] = []
            data['profile']['y'] = mat[0][:].tolist()
            data['profile']['z'] = mat[1][:].tolist()
        if mat.shape[0] == 3:
            data['profile']['x'] = mat[0][:].tolist()
            data['profile']['y'] = mat[1][:].tolist()
            data['profile']['z'] = mat[2][:].tolist()
        data['watercolumn'] = None
        if os.path.isfile(watercolumn_file):
            mat = np.loadtxt(watercolumn_file)
            data['watercolumn'] = mat
        data['profile_offset'] = None
        if os.path.isfile(profileoffset_file):
            mat = np.loadtxt(profileoffset_file)
            data['profile_offset'] = mat

    riveraxis, markers_worldcoordinates, profile = apply_transformations(data)
    write_data(currentpath + os.sep + "discharge_freehelper",
               riveraxis, markers_worldcoordinates, profile)

