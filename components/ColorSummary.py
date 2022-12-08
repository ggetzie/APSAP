import numpy as np
from  model.nn_segmentation import MaskPredictor
from PIL import Image
from misc import open_image 
import open3d as o3d
 

import math

ceremicPredictor = MaskPredictor("./model/ceremicsmask.pt")
colorgridPredictor = MaskPredictor("./model/colorgridmask.pt")
def get_brightness_summary_from_2d(image_path):
    image = open_image(image_path,full_size=False)
    masked = ceremicPredictor.predict(image)
    
    masked_ravel = (((np.array(masked).ravel()).astype(bool)))
    np_image = np.array(image.convert('L')).ravel()
 
    np_image[masked_ravel==False] = 0

  
    pixels_sorted = sorted(np_image[np_image!=0])
    
    median = (pixels_sorted[int(len(pixels_sorted)/2)])
    max_ = max(pixels_sorted)
    min_ = min(pixels_sorted)
    mean = (np.sum(pixels_sorted)/len(pixels_sorted))
    upper_q = pixels_sorted[int(len(pixels_sorted)* (3/4))]
    lower_q = pixels_sorted[int(len(pixels_sorted)* (1/4))]
    std = np.std(pixels_sorted)
    return (max_,min_,median, mean,upper_q, lower_q, std)
 
def get_brightness_summary_from_3d (model_path, vis):

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
    std = np.std(pixels_sorted)
    return (max_,min_,median, mean,upper_q, lower_q, std)
    
def get_color_summary_from_2d(image_path):
    image = open_image(image_path,full_size=False)
    masked = ceremicPredictor.predict(image)
    
    masked_ravel = (((np.array(masked)).astype(bool)))
 
    image_np = np.array(image)
    #These contains pixels with all the color in RGB
    pixels_color = (image_np[masked_ravel==True] )
    r = pixels_color[:, 0]
    g = pixels_color[:, 1]
    b = pixels_color[:, 2]
    
    r_mean = np.mean(r)
    g_mean = np.mean(g)
    b_mean = np.mean(b)

    return (r_mean, g_mean, b_mean)

def get_color_summary_from_3d (model_path, vis):

    current_pcd_load = o3d.io.read_point_cloud(model_path) 
    
    vis.add_geometry(current_pcd_load)
    ctr = vis.get_view_control()
        
    vis.get_render_option().point_size = 5

    ctr.change_field_of_view(step=-9)
    object_image = vis.capture_screen_float_buffer(True)
     
    pic =  np.multiply(np.array(object_image), 255) 
    
 
    all_channels_not_255 =~ (( pic[:, :, 0] == 255. ) &  (pic[:, :, 1 ] == 255. )  & (pic[:, :, 2] == 255. ) )
    pixels_color =  pic[all_channels_not_255] 
 
   
    r = pixels_color[:, 0]
    g = pixels_color[:, 1]
    b = pixels_color[:, 2]
    
    r_mean = np.mean(r)
    g_mean = np.mean(g)
    b_mean = np.mean(b)
 
    vis.remove_geometry(current_pcd_load)
    del ctr
    return (r_mean, g_mean, b_mean)
    
def srgb_color_difference(colors1, colors2):
    #https://en.wikipedia.org/wiki/Color_difference#sRGB

    if abs(colors1[0] - colors2[0]) < 128:
        
        return math.sqrt(2*( (colors2[0] - colors1[0])**2 ) + 4*( (colors2[1]  - colors1[1])**2 ) + 3 *( (colors2[2] - colors1[2])**2 ))
   
    else:
        return math.sqrt(2*( (colors2[0] - colors1[0])**2 ) + 4*( (colors2[1]  - colors1[1])**2 ) + 2 *( (colors2[2] - colors1[2])**2 ))

    
def get_color_difference(front_color, back_color, model_color ):

 
    
    color_diff_1 = srgb_color_difference(front_color, model_color)
    color_diff_2 = srgb_color_difference(back_color, model_color)
    
 
    biggest_color_difference = srgb_color_difference([255,255,255],[0,0,0]) /2 #The color difference wouldn't be two drastic. Let's clamp the value a bit
    return   biggest_color_difference / (biggest_color_difference - min(color_diff_1, color_diff_2)) 
 