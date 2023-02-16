
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

 
    


model_path = r"D:\ararat\data\files\N\38\478020\4419550\11\finds\3dbatch\2022\batch_000\registration_reso1_maskthres242\final_output\piece_0_world.ply"




def get_lumance_summary_2d(img_path):
    pic_f_image = Image.open(img_path).resize((450, 300), Image.LANCZOS)
    ceremicsmask_predictor = MaskPredictor("../computation/ceremicsmask.pt")
    #Getting the numpy arrys for the image and the mask
    img_mask_np = np.array(ceremicsmask_predictor.predict(pic_f_image))
    img_np = np.array(pic_f_image.convert('RGBA'))
    #Cleaning the background
    for i in range(len(img_mask_np)):
        for j in range(len(img_mask_np[0])):
           if img_mask_np[i][j]  <= 170:
                img_np[i][j][0] = 0
                img_np[i][j][1] = 0
                img_np[i][j][2] = 0
                img_np[i][j][3] = 0
    image =   Image.fromarray((img_np))

    np_image =np.array(image.convert('L')).ravel()
    
    #gather lumance summary
    lumance_summary = []
 
    for i in range(0, 256):
        lumance_summary.append(0)
    for luminance in np_image:
        if luminance != 0:
            lumance_summary[luminance] += 1
 
 
    return lumance_summary


def get_lumance_summary_3d(model_path):
    ply_window = o3d.visualization.Visualizer()

    ply_window.create_window(visible=False)   
    ply_window.get_render_option().light_on = False
    #load the model
    current_pcd_load = o3d.io.read_point_cloud(model_path) 
    ply_window.add_geometry(current_pcd_load)
    ctr = ply_window.get_view_control()    
    ply_window.get_render_option().point_size = 5
    ctr.change_field_of_view(step=-9)

    img_captured = ply_window.capture_screen_float_buffer(True)
    image_np =  np.multiply(np.array(object_image), 255).astype(np.uint8)
    img = Image.fromarray(image_np)

    img_np = np.array(img.convert('RGBA'))
    
    for i in range(len(img_np)):
        for j in range(len(img_np[0])):
           if img_np[i][j][0]  == 255 and img_np[i][j][1]  == 255 and img_np[i][j][2]  == 255:
                img_np[i][j][0] = 0
                img_np[i][j][1] = 0
                img_np[i][j][2] = 0
                img_np[i][j][3] = 0
    image =   Image.fromarray((img_np))

    np_image = np.array(image.convert('L')).ravel()
 

    #clean up the model

    ply_window.remove_geometry(current_pcd_load)
    del ctr

    #generate the summary and return the result
 
    
    #gather lumance summary
    lumance_summary = {}
    for i in range(0, 256):
        lumance_summary[i] = 0
    for luminance in np_image:
        if luminance != 0:
            lumance_summary[luminance] += 1
    return lumance_summary

all_images_urls = []
ceremicsmask_predictor = MaskPredictor("../computation/ceremicsmask.pt")
img_path = r"D:\ararat\data\files\N\38\478020\4419550\11\finds\individual\1\photos\1.jpg"
    
print(sum(get_lumance_summary_2d(img_path)))
 
