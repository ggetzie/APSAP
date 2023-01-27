import open3d as o3d 
import numpy as np
from misc import open_image, get_mask_pixel_width, get_ceremic_area
from  model.nn_segmentation import MaskPredictor



from PIL import Image
import open3d as o3d 
import numpy as np
from misc import open_image, get_mask_pixel_width, get_ceremic_area
from  model.nn_segmentation import MaskPredictor

import math


class Comparator:
    #This stores the functions associated getting the areas, brightness, colors, brightness's standard deviation and width-length pairs 
    # 
    
    def __init__(self, vis) -> None:

        self.vis = vis #o3d.visualization.Visualizer()
        self.ceremicPredictor = MaskPredictor("./model/ceremicsmask.pt")
        self.colorgridPredictor = MaskPredictor("./model/colorgridmask.pt")
        self.vis.get_render_option().light_on = False
        self.vis.get_render_option().point_size = 20 #If the point is too small, the picture taken will have a lot of holes
                                            #When we use our own field of view
 
    def get_3d_object_area_and_width_length(self, _3d_object_path):
        #Loading a bounding box to get the actual width length in cm and the pixel, we got the 
        vis = self.vis
        current_pcd_load = o3d.io.read_point_cloud(_3d_object_path) 
        bounding_box = current_pcd_load.get_axis_aligned_bounding_box() 
        bounding_box.color = (1,0,0)
        extents = (bounding_box.get_extent())
        length = (max(extents[0], extents[1]))
        width = min(extents[0],extents[1]) 
        bounding_box.color = (1,0,0)
        
        
        vis.add_geometry(bounding_box)
        ctr = vis.get_view_control()
        ctr.change_field_of_view(step=-9)
        bounding_box_pixels_difference = self.bounding_box_get_pixel_difference()
        bounding_box_width_mm = extents[0]
        vis.remove_geometry(bounding_box)
        #We now got 
        #When geomoetry is added camera is supposed to change, so we need to change the field of view again
        vis.add_geometry(current_pcd_load)
        ctr.change_field_of_view(step=-9)
        
        object_image = vis.capture_screen_float_buffer(True)
        object_image_array = np.multiply(np.array(object_image), 255).astype(np.uint8).reshape(-1, 3)

        object_image_array_object_locations =  ~((object_image_array==(255,255,255)).all(axis=-1))   

        pixel_counts = (np.count_nonzero(object_image_array_object_locations))
        mm_pixels_ratio = bounding_box_width_mm/bounding_box_pixels_difference
        
         
        #Cleanup
        vis.remove_geometry(current_pcd_load)
        del ctr
        
        area = ((mm_pixels_ratio ** 2 )* pixel_counts)/100 
        return (area), ((width,length))        
    def get_2d_picture_area(self, _2d_picture_path):
        image = open_image(_2d_picture_path, full_size=False)
        mask_image = self.colorgridPredictor.predict(image)
        mm_per_pixel =  53.98 /get_mask_pixel_width(mask_image)  #53.98 is the width of the credit-card size color grid
        ceremic_mask = self.ceremicPredictor.predict(image) 
        tif_area =  get_ceremic_area(ceremic_mask, mm_per_pixel)
        return tif_area
    
 
    def compare_3d_with_2d(self,_3d_object_path, _2d_picture_path):
        _3d_area = self.get_3d_object_area(_3d_object_path)
        _2d_area = self.get_2d_picture_area(_2d_picture_path)
        return  (max(_3d_area/_2d_area, _2d_area/ _3d_area))
 

 
    def bounding_box_get_pixel_difference(self ):
        #Detecting the length of bounding box to get the correct ratio

        vis = self.vis
      
                
        vis.get_render_option().point_size = 5
        red_box_image = vis.capture_screen_float_buffer(True)
 

        red_box_image_array = np.multiply(np.array(red_box_image), 255).astype(np.uint8)
        red_box_mid_y = red_box_image_array.shape[0]

        red_box_middle_row = red_box_image_array[int(red_box_mid_y/2)]
        
        red_box_middle_row_red_locations = ~((red_box_middle_row[:,0] == 255) & (red_box_middle_row[:,1] == 255)  & (red_box_middle_row[:,2] == 255))
        red_box_red_locations = np.where(red_box_middle_row_red_locations)[0]
        #Here we get the pixel to cm ratio
        pixels_difference = (red_box_red_locations[2] - red_box_red_locations[1] ) #* 0.9
        
        return  pixels_difference

    def get_2d_width_length(self,path_2d):
        image = open_image(path_2d,full_size=False)
        masked_ceremics = self.ceremicPredictor.predict(image)
        masked_ceremics_bool = (((np.array(masked_ceremics)).astype(bool)))
        mask_grid = self.colorgridPredictor.predict(image)
        mm_per_pixel =  53.98 /get_mask_pixel_width(mask_grid)  #53.98 is the width of the credit-card size color grid
        indices = (np.nonzero(masked_ceremics_bool))
        sorted_y_indices = sorted(indices[0])
        sorted_x_indices = sorted(indices [1])
    
        y_diff =  abs(sorted_y_indices[-1] - sorted_y_indices[0]) * mm_per_pixel
        x_diff = abs(sorted_x_indices[-1] - sorted_x_indices[0] ) * mm_per_pixel 
        width = min(y_diff, x_diff)
        length = max(y_diff,x_diff)
        return width , length 
        
 

    def get_brightness_summary_from_2d(self, image_path):
        image = open_image(image_path,full_size=False)
        masked = self.ceremicPredictor.predict(image)
        
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
        return (int(max_),int(min_),int(median), (mean),int(upper_q), int(lower_q), (std))
    
    def get_brightness_summary_from_3d (self, model_path):
        vis = self.vis
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
        
    def get_color_summary_from_2d(self, image_path):
        image = open_image(image_path,full_size=False)
        masked = self.ceremicPredictor.predict(image)
        
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

    def get_color_summary_from_3d (self, model_path):
        vis = self.vis
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
        return (float(r_mean), float(g_mean), float(b_mean))
        
    def srgb_color_difference(self, colors1, colors2):
        #https://en.wikipedia.org/wiki/Color_difference#sRGB

        if abs(colors1[0] - colors2[0]) < 128:
            
            return math.sqrt(2*( (colors2[0] - colors1[0])**2 ) + 4*( (colors2[1]  - colors1[1])**2 ) + 3 *( (colors2[2] - colors1[2])**2 ))
    
        else:
            return math.sqrt(2*( (colors2[0] - colors1[0])**2 ) + 4*( (colors2[1]  - colors1[1])**2 ) + 2 *( (colors2[2] - colors1[2])**2 ))

        

    