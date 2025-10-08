import xarray as xr
import pyorc
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import json


def load_frame(video_file: str, frame_idx: int = 0):
    """
    Load a frame from the video.
    """
    video = pyorc.Video(video_file, start_frame=frame_idx, end_frame=frame_idx+1)
    frame = video.get_frame(frame_idx, method="rgb")
    return frame


def plot_frame(frame, gcps_src=None, corners=None, save_path=None):
    """
    Plot frame with optional GCPs and AOI corners.
    """
    f = plt.figure(figsize=(10, 6))
    plt.imshow(frame)

    if gcps_src:
        plt.plot(*zip(*gcps_src), "rx", markersize=20, label="Control points")
    if corners:
        plt.plot(*zip(*corners), "co", label="Corners of AOI")

    plt.legend()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=72)
    plt.close("all")


def build_camera_config(frame, gcps, crs=32735, resolution=0.01, window_size=25, corners=None):
    """
    Create a camera configuration using GCPs and optional AOI corners.
    """
    height, width = frame.shape[0:2]

    cam_config = pyorc.CameraConfig(height=height, width=width, gcps=gcps, crs=crs)
    if corners:
        cam_config.set_bbox_from_corners(corners)
    cam_config.resolution = resolution
    cam_config.window_size = window_size

    return cam_config


def plot_camera_config(cam_config, frame=None, save_path=None):
    """
    Plot camera configuration in 2D and optionally overlay on frame.
    """
    ax1 = cam_config.plot(tiles="GoogleTiles", tiles_kwargs={"style": "satellite"})

    if frame is not None:
        f = plt.figure()
        ax2 = plt.axes()
        ax2.imshow(frame)
        cam_config.plot(ax=ax2, camera=True)

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=72)

    plt.close("all")


def plot_camera_3d(cam_config, save_path=None):
    """
    Plot camera configuration in 3D.
    """
    f = plt.figure(figsize=(12, 7))
    ax = f.add_subplot(projection="3d")
    cam_config.plot(mode="3d", ax=ax)
    ax.set_aspect("equal")

    if save_path:
        plt.savefig(save_path, bbox_inches="tight", dpi=72)

    plt.close("all")


def export_camera_config(cam_config, filename="cam_config.json"):
    """
    Export camera configuration to JSON file.
    """
    cam_config.to_file(filename)
    return filename


# ================= Example usage =================
if __name__ == "__main__":
    video_file = "ngwerere_20191103.mp4"
    frame = load_frame(video_file)

    gcps = dict(
        src=[
            [1421, 1001],
            [1251, 460],
            [421, 432],
            [470, 607]
        ],
        dst=[
            [642735.8076, 8304292.1190],
            [642737.5823, 8304295.593],
            [642732.7864, 8304298.4250],
            [642732.6705, 8304296.8580]
        ],
        z_0=1182.2
    )

    corners = [
        [292, 817],
        [50, 166],
        [1200, 236],
        [1600, 834]
    ]

    # Step 1: Plot raw frame
    plot_frame(frame, gcps_src=gcps["src"], corners=corners, save_path="frame_plot.jpg")

    # Step 2: Build camera config
    cam_config = build_camera_config(frame, gcps=gcps, corners=corners)

    # Step 3: Plot camera config
    plot_camera_config(cam_config, frame=frame, save_path="ngwerere_camconfig.jpg")

    # Step 4: Plot 3D camera config
    plot_camera_3d(cam_config, save_path="ngwerere_camconfig_3d.jpg")

    # Step 5: Export config
    export_camera_config(cam_config, "ngwerere.json")

    print("Processing complete. Config saved at ngwerere.json")



