

import numpy as np
from  model.nn_segmentation import MaskPredictor
from PIL import Image
from misc import open_image, get_mask_pixel_width, get_ceremic_area
import open3d as o3d


ceremicPredictor = MaskPredictor("./model/ceremicsmask.pt")
colorgridPredictor = MaskPredictor("./model/colorgridmask.pt")
def get_image_summary_from_2d(image_path):
    image = open_image(image_path,full_size=False)
    masked = ceremicPredictor.predict(image)
    
    masked_ravel = (((np.array(masked).ravel()).astype(bool)))
    np_image = np.array(image.convert('L')).ravel()
    #print(np_image)
    np_image[masked_ravel==False] = 0

  
    pixels_sorted = sorted(np_image[np_image!=0])
    median = (pixels_sorted[int(len(pixels_sorted)/2)])
    max_ = max(pixels_sorted)
    min_ = min(pixels_sorted)
    mean = (np.sum(pixels_sorted)/len(pixels_sorted))
    upper_q = pixels_sorted[int(len(pixels_sorted)* (3/4))]
    lower_q = pixels_sorted[int(len(pixels_sorted)* (1/4))]
    return (max_,min_,median, mean,upper_q, lower_q)
 
def get_image_summary_from_3d (model_path, vis):

    current_pcd_load = o3d.io.read_point_cloud(model_path) 
    
    vis.add_geometry(current_pcd_load)
    ctr = vis.get_view_control()
        
    vis.get_render_option().point_size = 5

    ctr.change_field_of_view(step=-9)
    object_image = vis.capture_screen_float_buffer(True)
     
    pic = (np.array(Image.fromarray( np.multiply(np.array(object_image), 255).astype(np.uint8)).convert('L')).ravel())
    pic[pic==255] = 0
    pixels_sorted = sorted(pic[pic!=0])
    median = (pixels_sorted[int(len(pixels_sorted)/2)])
    max_ = max(pixels_sorted)
    min_ = min(pixels_sorted)
    mean = (np.sum(pixels_sorted)/len(pixels_sorted))
    upper_q = pixels_sorted[int(len(pixels_sorted)* (3/4))]
    lower_q = pixels_sorted[int(len(pixels_sorted)* (1/4))]
    vis.remove_geometry(current_pcd_load)
    del ctr
    return (max_,min_,median, mean,upper_q, lower_q)
    