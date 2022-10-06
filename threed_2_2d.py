"""
3d_2_2d.py
The file contains functions that produce front and back images of a ceramic sherd based on an existing 3d model (ply file).
It has three functions for 3 levels of batch operation: context level, batch level, or individual level
"""

# opengl not supported by remote server. Use the Mesa version of opengl, for cpu based software rendering
# import ctypes
# ctypes.cdll.LoadLibrary('C:\\Users\\bzichen\\.conda\\envs\\piecereg\\Lib\\site-packages\\open3d\\cpu\\opengl32.dll')

import open3d as o3d
import numpy as np
import copy
import pathlib
import re


def open_interactive_model(model_path):
    # read the point cloud
    pcd = o3d.io.read_point_cloud(str(model_path))
    pcddown = pcd.voxel_down_sample(voxel_size=0.3)
    o3d.visualization.draw_geometries(width=800, height=600, geometry_list=[pcddown])


# create front and back images from one finished 3d ply file of a single piece in a file
# model path should be a path file of the full path of the ply file
def proccess_one_model(model_path):
    # get piece number from name
    model_name = model_path.stem
    model_number = re.search("_\d+_", model_name)
    if model_number:
        model_number = model_number.group(0).replace("_", "")
    else:
        print("read wrong 3d mdoel file")

    # create folders for image outputs under the folder with ply files
    output_folder = model_path.parent.joinpath("individual_images", model_number)
    output_folder.mkdir(parents=True, exist_ok=True)

    # read the point cloud
    pcd = o3d.io.read_point_cloud(str(model_path))

    # copy and flip the point cloud by rotating around y axis
    pcd_back = copy.deepcopy(pcd)
    R = pcd_back.get_rotation_matrix_from_xyz((0, np.pi, 0))
    pcd_back.rotate(R, center=(0, 0, 0))

    # visualize and screenshot the front side
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False)
    vis.add_geometry(pcd)
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(str(output_folder) + "\\2d_image_front.png")
    vis.remove_geometry(pcd)

    # visualize and screenshot the back side
    vis.add_geometry(pcd_back)
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(str(output_folder) + "\\2d_image_back.png")

    vis.destroy_window()


# process a whole batch
# input argument should be a path file of the full path of the batch folder
def process_one_batch(batch_folder):

    models_folder = batch_folder.joinpath(
        "registration_reso1_maskthres242", "final_output"
    )

    # make sure final_output folder exists
    if not models_folder.exists():
        print("Batch has not finished building all the 3d models")
    else:
        piece_model_list = [
            file for file in models_folder.iterdir() if file.suffix == ".ply"
        ]  # read in all the files
        piece_model_pcd_list = [
            file for file in piece_model_list if file.stem[-1] == "d"
        ]  # keep only the first pointclouds, modify as needed

        # check having read in the correct number of ply file
        if (len(piece_model_pcd_list) == 0) or (len(piece_model_list) % 3 != 0):
            print("number of ply files are is not correct")
        else:
            for piece_model in piece_model_pcd_list:
                proccess_one_model(piece_model)


# process a whole context
# innput argument should be the path to the trench folder and the relevant context number
# note that this context requires more error or edge case handling given that there probably are many expected files missing in one context given the scale
def process_one_context(trench_path, context_number):
    context_folder = pathlib.Path(trench_path).joinpath(
        str(context_number), "finds", "3dbatch", "2022"
    )
    # double check folde exists
    if not context_folder.exists():
        print("Batch has not finished building all the 3d models")
    else:
        batch_list = [
            batch
            for batch in context_folder.iterdir()
            if (
                batch.is_dir()
                and ("batch" in batch.stem)
                and ("einscan" not in batch.stem)
            )
        ]  # read in all the files

        for one_batch in batch_list:
            process_one_batch(one_batch)


##Using 478130/4419430/43 as a test, change as needed
def testing():
    # trench_path = r'D:\\ararat\\data\\files\\N\\38\\478130\\4419430\\'
    # context_number = '43'

    # process_one_context(trench_path, context_number)

    path = pathlib.Path(
        r"D:\ararat\data\files\N\38\478130\4419430\43\finds\3dbatch\2022\batch_000\registration_reso1_maskthres242\final_output\piece_0_world.ply"
    )
    # proccess_one_model(path)
    open_interactive_model(path)


# testing()
