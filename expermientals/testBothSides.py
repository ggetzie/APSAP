
import ctypes

opengl_path = "../computation/opengl32.dll"
ctypes.cdll.LoadLibrary(opengl_path)
import open3d as o3d
import numpy as np
from PIL import Image
import imagehash
import sys
sys.path.insert(0,'..')
from computation.nn_segmentation import MaskPredictor
import matplotlib.pyplot as plt

np.set_printoptions(suppress=True)


from debug_database import get_all_pottery_sherd_info

from pathlib import Path

ply_window = o3d.visualization.Visualizer()
model_path = "./piece_0_world.ply"
ply_window.create_window(visible=False, width=430, height=390)   
ply_window.get_render_option().light_on = False
#load the model
current_pcd_load = o3d.io.read_point_cloud(model_path) 
ply_window.add_geometry(current_pcd_load)
ctr = ply_window.get_view_control()    
ply_window.get_render_option().point_size = 5
ctr.change_field_of_view(step=-9)

img_captured = ply_window.capture_screen_float_buffer(True)
image_np =  np.multiply(np.array(img_captured), 255).astype(np.uint8)
img = Image.fromarray(image_np)
img.save("front.png")
ply_window.remove_geometry(current_pcd_load)
del ctr

ply_window.add_geometry(current_pcd_load)
ctr = ply_window.get_view_control()    
ply_window.get_render_option().point_size = 5
ctr.change_field_of_view(step=-9)

img_captured = ply_window.capture_screen_float_buffer(True)
image_np =  np.multiply(np.array(img_captured), 255).astype(np.uint8)
img = Image.fromarray(image_np)