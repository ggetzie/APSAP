from  computation.nn_segmentation import MaskPredictor
from scipy.ndimage import binary_dilation
from PIL import Image
import open3d as o3d 
import numpy as np
import smallestenclosingcircle
 
class Measure3dMixin:  # bridging the view(gui) and the model(data)
 

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
        if(len(red_box_red_locations)>=4):

            pixels_difference = (red_box_red_locations[2] - red_box_red_locations[1] ) #* 0.9
        else :
            pixels_difference = (red_box_red_locations[1] - red_box_red_locations[0] ) #* 0.9
        return  pixels_difference

    def get_contour_3d (self,  model_path):
        import numpy as np
        import open3d as o3d
        from PIL import Image
        import cv2
        main_model, main_view, main_presenter = self.get_model_view_presenter()    

        ply_window = main_view.ply_window
        ply_window.clear_geometries()
        current_pcd_load = o3d.io.read_point_cloud(model_path) 
        
        ply_window.add_geometry(current_pcd_load)
        ctr = ply_window.get_view_control()
            
        ply_window.get_render_option().point_size = 5

        ctr.change_field_of_view(step=-9)
        object_image = ply_window.capture_screen_float_buffer(True)
        
        pic = np.array(Image.fromarray( np.multiply(np.array(object_image), 255).astype(np.uint8)).convert('L'))#(np.array(Image.fromarray( np.multiply(np.array(object_image), 255).astype(np.uint8)).convert('L')).ravel())
        pic[pic==255] = 0
        pic[pic != 0] = 255
        
        pil_image = Image.fromarray(pic).convert("RGB")
      
        open_cv_image = np.array(pil_image) 
    # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        img_gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        ret, thresh = cv2.threshold(img_gray, 127, 255,0)
        contours, hierarchy  = cv2.findContours(thresh,2,1)
        cnt1 = contours[0]
        ply_window.remove_geometry(current_pcd_load)
        del ctr
        return cnt1