from  computation.nn_segmentation import MaskPredictor
from scipy.ndimage import binary_dilation
from PIL import Image
import open3d as o3d 
import numpy as np
import smallestenclosingcircle
 
class MeasurePixels3DDataMixin:  # bridging the view(gui) and the model(data)

    def get_3d_area_circle_ratio(self, _3d_object_path) -> float:
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        area_in_pixels= main_presenter.get_3d_object_area_in_pixels(_3d_object_path)
        circle_in_pixels = main_presenter.get_3d_object_circle_in_pixels(_3d_object_path)
        return area_in_pixels/circle_in_pixels

        
    def get_3d_object_area_in_pixels(self, _3d_object_path) -> int:
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        
        current_pcd_load = o3d.io.read_point_cloud(_3d_object_path) 
        main_view.ply_window.add_geometry(current_pcd_load)
        ctr = main_view.ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)
        object_image = main_view.ply_window.capture_screen_float_buffer(True)
        object_image_array = np.multiply(np.array(object_image), 255).astype(np.uint8).reshape(-1, 3)
  
        object_image_array_object_locations =  ~((object_image_array==(255,255,255)).all(axis=-1))    
        pixel_counts = (np.count_nonzero(object_image_array_object_locations))
   

        main_view.ply_window.remove_geometry(current_pcd_load)
        del ctr
        
        return pixel_counts



    def get_3d_object_circle_in_pixels(self, _3d_object_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

      
        current_pcd_load = o3d.io.read_point_cloud(_3d_object_path) 
        main_view.ply_window.add_geometry(current_pcd_load)
        ctr = main_view.ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)
        object_image = main_view.ply_window.capture_screen_float_buffer(True)
        object_image_array = np.multiply(np.array(object_image), 255).astype(np.uint8) 
     
        _1_white_other_0 = (~((object_image_array[:, :, 0] == 255 ) & (object_image_array[:, :, 1] == 255 )& (object_image_array[:, :, 2] == 255))).astype(int)
       
        
    
        k = np.ones((3,3),dtype=int)
        boundary_array = binary_dilation(_1_white_other_0==0, k) & _1_white_other_0
        #Here we get the x, y coordinates of the boundary(which is the non zeros values of the 2d array)
        nonzeros_x_ys = np.nonzero(boundary_array)
        #Tuples of all indices of the boundary
        indices_tuples = list(zip(nonzeros_x_ys[0], nonzeros_x_ys[1]))
        #Below is a nested O(n^2) for loop that gets
        new_li = []
        threshold = 100
        for i in range(len(indices_tuples)): #For each of the tuple, compared it to all the tuples added before, if they are close in distance, don't add to it.
            addable = True
            for pairs in new_li:
                if( (pairs[0] - indices_tuples[i][0])**2  +  (pairs[1] - indices_tuples[i][1])**2  < threshold):
                    addable = False
                    break
            if(addable == True):
                new_li.append(indices_tuples[i])
        center_x, center_y, radius = smallestenclosingcircle.make_circle(new_li)
        main_view.ply_window.remove_geometry(current_pcd_load)

        del ctr
        return (radius**2 ) * 3.1416
   

    def get_3d_object_area_and_width_length(self, _3d_object_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        #Loading a bounding box to get the actual width length in cm and the pixel, we got the 
        ply_window = main_view.ply_window
        current_pcd_load = o3d.io.read_point_cloud(_3d_object_path) 
        bounding_box = current_pcd_load.get_axis_aligned_bounding_box() 
        bounding_box.color = (1,0,0)
        extents = (bounding_box.get_extent())
        length = (max(extents[0], extents[1]))
        width = min(extents[0],extents[1]) 
        bounding_box.color = (1,0,0)
        
        
        ply_window.add_geometry(bounding_box)
        ctr = ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)
        bounding_box_pixels_difference = main_presenter.bounding_box_get_pixel_difference()
        bounding_box_width_mm = extents[0]
        ply_window.remove_geometry(bounding_box)
        #We now got 
        #When geomoetry is added camera is supposed to change, so we need to change the field of view again
        ply_window.add_geometry(current_pcd_load)
        ctr.change_field_of_view(step=-9)
        
        object_image = ply_window.capture_screen_float_buffer(True)
        object_image_array = np.multiply(np.array(object_image), 255).astype(np.uint8).reshape(-1, 3)

        object_image_array_object_locations =  ~((object_image_array==(255,255,255)).all(axis=-1))   

        pixel_counts = (np.count_nonzero(object_image_array_object_locations))
        mm_pixels_ratio = bounding_box_width_mm/bounding_box_pixels_difference
        
         
        #Cleanup
        ply_window.remove_geometry(current_pcd_load)
        del ctr
        
        area = ((mm_pixels_ratio ** 2 )* pixel_counts)/100 
        return (area), ((width,length))        



    def bounding_box_get_pixel_difference(self ):
        #Detecting the length of bounding box to get the correct ratio
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        ply_window = main_view.ply_window
      
                
        ply_window.get_render_option().point_size = 5
        red_box_image = ply_window.capture_screen_float_buffer(True)
 

        red_box_image_array = np.multiply(np.array(red_box_image), 255).astype(np.uint8)
        red_box_mid_y = red_box_image_array.shape[0]

        red_box_middle_row = red_box_image_array[int(red_box_mid_y/2)]
        
        red_box_middle_row_red_locations = ~((red_box_middle_row[:,0] == 255) & (red_box_middle_row[:,1] == 255)  & (red_box_middle_row[:,2] == 255))
        red_box_red_locations = np.where(red_box_middle_row_red_locations)[0]
        #Here we get the pixel to cm ratio
        pixels_difference = (red_box_red_locations[2] - red_box_red_locations[1] ) #* 0.9
        
        return  pixels_difference

    def get_brightness_summary_from_3d (self, model_path):

        main_model, main_view, main_presenter = self.get_model_view_presenter()

        ply_window = main_view.ply_window
        current_pcd_load = o3d.io.read_point_cloud(model_path) 
        
        ply_window.add_geometry(current_pcd_load)
        ctr = ply_window.get_view_control()
            
        ply_window.get_render_option().point_size = 5

        ctr.change_field_of_view(step=-9)
        object_image = ply_window.capture_screen_float_buffer(True)
        
        pic = (np.array(Image.fromarray( np.multiply(np.array(object_image), 255).astype(np.uint8)).convert('L')).ravel())
        pic[pic==255] = 0
        pixels_sorted = sorted(pic[pic!=0])
        median = (pixels_sorted[int(len(pixels_sorted)/2)])
        max_ = max(pixels_sorted)
        min_ = min(pixels_sorted)
        mean = (np.sum(pixels_sorted)/len(pixels_sorted))
        upper_q = pixels_sorted[int(len(pixels_sorted)* (3/4))]
        lower_q = pixels_sorted[int(len(pixels_sorted)* (1/4))]
        ply_window.remove_geometry(current_pcd_load)
        del ctr
        std = np.std(pixels_sorted)
        return (max_,min_,median, mean,upper_q, lower_q, std)
        
    def get_color_summary_from_3d (self, model_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        
        ply_window = main_view.ply_window
        current_pcd_load = o3d.io.read_point_cloud(model_path) 
        
        ply_window.add_geometry(current_pcd_load)
        ctr = ply_window.get_view_control()
            
        ply_window.get_render_option().point_size = 5

        ctr.change_field_of_view(step=-9)
        object_image = ply_window.capture_screen_float_buffer(True)
        
        pic =  np.multiply(np.array(object_image), 255) 
        
    
        all_channels_not_255 =~ (( pic[:, :, 0] == 255. ) &  (pic[:, :, 1 ] == 255. )  & (pic[:, :, 2] == 255. ) )
        pixels_color =  pic[all_channels_not_255] 
    
    
        r = pixels_color[:, 0]
        g = pixels_color[:, 1]
        b = pixels_color[:, 2]
        
        r_mean = np.mean(r)
        g_mean = np.mean(g)
        b_mean = np.mean(b)
    
        ply_window.remove_geometry(current_pcd_load)
        del ctr
        return (float(r_mean), float(g_mean), float(b_mean))
 
    def get_hamming_hash_from_3d(self, path):

 
        return 0