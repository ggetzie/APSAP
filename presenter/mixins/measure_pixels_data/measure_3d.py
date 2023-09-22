from  computation.nn_segmentation import MaskPredictor
from scipy.ndimage import binary_dilation
from PIL import Image
import open3d as o3d 
import numpy as np
import smallestenclosingcircle
import cv2
class Measure3dMixin:  # bridging the view(gui) and the model(data)
 

    def get_area_width_length_contour3d(self, _3d_object_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        
        #Loading a bounding box to get the actual width length in cm and the pixel, we got the 
        ply_window = main_view.ply_window
        ply_window.get_render_option().point_size = 5
        ctr = ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)
        


        current_pcd_load = o3d.io.read_point_cloud(_3d_object_path) 
        bounding_box = current_pcd_load.get_axis_aligned_bounding_box() 
        bounding_box.color = (1,0,0)
        ply_window.add_geometry(bounding_box)
        (width_3d, length_3d) = main_presenter.get_width_length_3d(bounding_box)
        mm_pixels_ratio = main_presenter.get_mm_pixels_ratio(bounding_box, ply_window)
        ply_window.remove_geometry(bounding_box)

        ply_window.add_geometry(current_pcd_load)
        (area_3d) = main_presenter.get_area_3d(ply_window,mm_pixels_ratio)
       
        (contour3d) = main_presenter.get_contour_3d(ply_window)        
       
        ply_window.remove_geometry(current_pcd_load)
        del ctr
        
        
        return (area_3d, width_3d, length_3d ,contour3d)      

    
    def get_width_length_3d(self, bounding_box):
        extents = (bounding_box.get_extent())
        width_3d = min(extents[0],extents[1]) 
        length_3d = (max(extents[0], extents[1]))
        return (width_3d, length_3d)
                
    def get_mm_pixels_ratio(self, bounding_box, ply_window):
        
        ply_window.get_render_option().point_size = 5
        ctr = ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)
        
        red_box_image = ply_window.capture_screen_float_buffer(True)
  
        red_box_image_array = np.multiply(np.array(red_box_image), 255).astype(np.uint8)
        red_box_mid_y = red_box_image_array.shape[0]

        red_box_middle_row = red_box_image_array[int(red_box_mid_y/2)]
        
        red_box_middle_row_red_locations = ~((red_box_middle_row[:,0] == 255) & (red_box_middle_row[:,1] == 255)  & (red_box_middle_row[:,2] == 255))
        red_box_red_locations = np.where(red_box_middle_row_red_locations)[0]
        #Here we get the pixel to cm ratio
        if(len(red_box_red_locations)>=4):

            bounding_box_pixels_difference = (red_box_red_locations[2] - red_box_red_locations[1] ) #* 0.9
        else :
            bounding_box_pixels_difference = (red_box_red_locations[1] - red_box_red_locations[0] ) #* 0.9
        bounding_box_width_mm = bounding_box.get_extent()[0]
        
        return bounding_box_width_mm/bounding_box_pixels_difference

    def get_area_3d(self, ply_window, mm_pixels_ratio):
        ply_window.get_render_option().point_size = 5
        ctr = ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)
        
        
        object_image = ply_window.capture_screen_float_buffer(True)
        object_image_array = np.multiply(np.array(object_image), 255).astype(np.uint8).reshape(-1, 3)

        object_image_array_object_locations =  ~((object_image_array==(255,255,255)).all(axis=-1))   

        pixel_counts = (np.count_nonzero(object_image_array_object_locations))
        area_3d = ((mm_pixels_ratio ** 2 )* pixel_counts)/100 
        return area_3d

    def get_contour_3d(self, ply_window):
        ply_window.get_render_option().point_size = 5
        ctr = ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)
        
        object_image = ply_window.capture_screen_float_buffer(True)
        
        pic = np.array(Image.fromarray( np.multiply(np.array(object_image), 255).astype(np.uint8)).convert('L')) 
        pic[pic==255] = 0
        pic[pic != 0] = 255
        
        ret, thresh = cv2.threshold(pic, 127, 255,0)
        contours, hierarchy  = cv2.findContours(thresh,2,1)
        contour3d = contours[0]  
        return contour3d


