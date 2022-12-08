
import numpy as np
from  model.nn_segmentation import MaskPredictor
from PIL import Image
from misc import open_image, get_mask_pixel_width, get_ceremic_area
import open3d as o3d
from skimage.color import rgb2lab, deltaE_cie76

import math

ceremicPredictor = MaskPredictor("./model/ceremicsmask.pt")
colorgridPredictor = MaskPredictor("./model/colorgridmask.pt")
# We compare the length(the longer side) and the width(the shorter side)

def get_2d_width_length(path_2d):
    image = open_image(path_2d,full_size=False)
    masked_ceremics = ceremicPredictor.predict(image)
    masked_ceremics_bool = (((np.array(masked_ceremics)).astype(bool)))
    mask_grid = colorgridPredictor.predict(image)
    mm_per_pixel =  53.98 /get_mask_pixel_width(mask_grid)  #53.98 is the width of the credit-card size color grid
    indices = (np.nonzero(masked_ceremics_bool))
    sorted_y_indices = sorted(indices[0])
    sorted_x_indices = sorted(indices [1])
 
    y_diff =  abs(sorted_y_indices[-1] - sorted_y_indices[0]) * mm_per_pixel
    x_diff = abs(sorted_x_indices[-1] - sorted_x_indices[0] ) * mm_per_pixel 
    width = min(y_diff, x_diff)
    length = max(y_diff,x_diff)
    return width , length 
    
def get_3d_width_length(path_3d, vis):

    current_pcd_load = o3d.io.read_point_cloud(path_3d) 
    
    bounding_box = current_pcd_load.get_axis_aligned_bounding_box() 
    bounding_box.color = (1,0,0)
    extents = (bounding_box.get_extent())
    length = (max(extents[0], extents[1]))
    width = min(extents[0],extents[1]) 
    #Remember we assume that the width and length of bounding box do not change too much because of the orientations
    
    return width, length