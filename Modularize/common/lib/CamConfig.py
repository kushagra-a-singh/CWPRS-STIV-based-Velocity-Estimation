import xarray as xr
import pyorc
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt


def CamConfig(VideoPath , gcps_dict , corners_list , output_path):

    video_file = VideoPath # Parameter 1 for function 
    video = pyorc.Video(video_file, start_frame=0, end_frame=1)  # we only need one frame
    frame = video.get_frame(0, method="rgb")


    # Dict as parameter 2 (src,dst,z_0,)
    gcps = gcps_dict

    height, width = frame.shape[0:2]
    cam_config = pyorc.CameraConfig(height=height, width=width, gcps=gcps, crs=32735)


    # Parameter 3 - List of x,y coords of vertices of bounding box 
    corners = corners_list

    cam_config.set_bbox_from_corners(corners)
    cam_config.resolution = 0.01
    cam_config.window_size = 25

    if output_path : 
        cam_config.to_file(output_path)

    return cam_config 