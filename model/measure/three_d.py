from pathlib import Path

import cv2
import numpy as np
import open3d as o3d
from PIL import Image


def get_3d_measurements(a3dmodel_path: Path, ply_window):
    """Find the area, width, length, and contour of the 3d model

    Args:
        a3dmodel_path (pathlib.Path): the path to the 3d model ply file
        ply_window (visualizer): An open3d visualizer window
        returns (width, length, area, contour): The width, length, area, and contour of the 3d model
    """
    # make sure the window is clear
    ply_window.clear_geometries()
    ply_window.get_render_option().point_size = 5
    ctr = ply_window.get_view_control()
    ctr.change_field_of_view(step=-9)

    point_cloud = o3d.io.read_point_cloud(a3dmodel_path)
    bounding_box = point_cloud.get_axis_aligned_bounding_box()
    bounding_box.color = (1, 0, 0)

    extents = bounding_box.get_extent()
    width = min(extents[0], extents[1])
    length = max(extents[0], extents[1])

    # find the ratio of mm to pixels for the ply_window
    ply_window.add_geometry(bounding_box)
    bb_image = ply_window.capture_screen_float_buffer(True)
    bb_array = np.multiply(np.array(bb_image), 255).astype(np.uint8)
    middle_row = bb_array[int(bb_array.shape[0] / 2)]
    middle_red_locations = ~(
        (middle_row[:, 0] == 255)
        & (middle_row[:, 1] == 255)
        & (middle_row[:, 2] == 255)
    )

    red_locations = np.where(middle_red_locations)[0]
    pixel_difference = (
        (red_locations[2] - red_locations[1])
        if len(red_locations) >= 4
        else (red_locations[1] - red_locations[0])
    )
    mm_per_pixel = width / pixel_difference

    # find the area of the 3d model
    ply_window.clear_geometries()
    ply_window.add_geometry(point_cloud)
    object_image = ply_window.capture_screen_float_buffer(True)
    object_array = np.multiply(np.array(object_image), 255).astype(np.uint8)
    object_array_locations = ~((object_array == (255, 255, 255)).all(axis=1))
    pixel_counts = np.count_nonzero(object_array_locations)
    area = (mm_per_pixel**2) * pixel_counts / 100

    # find the contour of the 3d model
    bw_image = np.array(Image.fromarray(object_array).convert("L"))
    # invert the image
    bw_image[bw_image == 255] = 0
    bw_image[bw_image != 0] = 255
    _, thresh = cv2.threshold(bw_image, 127, 255, 0)
    contours, _ = cv2.findContours(thresh, 2, 1)
    contour = contours[0]
    return width, length, area, contour
