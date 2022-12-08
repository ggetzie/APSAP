import open3d as o3d 
import numpy as np
from misc import open_image, get_mask_pixel_width, get_ceremic_area
from  model.nn_segmentation import MaskPredictor




import open3d as o3d 
import numpy as np
from misc import open_image, get_mask_pixel_width, get_ceremic_area
from  model.nn_segmentation import MaskPredictor




class AreaComparator:
    def __init__(self, vis) -> None:

        self.vis = vis #o3d.visualization.Visualizer()
        self.ceremicPredictor = MaskPredictor("./model/ceremicsmask.pt")
        self.colorgridPredictor = MaskPredictor("./model/colorgridmask.pt")
        self.vis.get_render_option().light_on = False
        self.vis.get_render_option().point_size = 20 #If the point is too small, the picture taken will have a lot of holes
                                            #When we use our own field of view
 
    def get_3d_object_area(self, _3d_object_path):
        vis = self.vis
         

        current_pcd_load = o3d.io.read_point_cloud(_3d_object_path) 
        #Bounding box is used to adjust the reference square to the correct z position
        bounding_box = current_pcd_load.get_axis_aligned_bounding_box() 
        bounding_box.color = (1,0,0)
        vis.add_geometry(bounding_box)
        ctr = vis.get_view_control()
    
        bounding_box_width_mm, bounding_box_pixels_difference = (self.bounding_box_get_pixel_difference(vis, bounding_box, ctr))
        vis.add_geometry(current_pcd_load)

        ctr.change_field_of_view(step=-9)
        object_image = vis.capture_screen_float_buffer(True)
        object_image_array = np.multiply(np.array(object_image), 255).astype(np.uint8).reshape(-1, 3)
        object_image_array_object_locations = ~(((object_image_array[:,0] == 255) & (object_image_array[:,1] == 255)  & (object_image_array[:,2] == 255))|((object_image_array[:,0] == 255) & (object_image_array[:,1] == 0)  & (object_image_array[:,2] == 0)))

        pixel_counts = (np.count_nonzero(object_image_array_object_locations))
        mm_pixels_ratio = bounding_box_width_mm/bounding_box_pixels_difference
        
         
        vis.remove_geometry(bounding_box)
        vis.remove_geometry(current_pcd_load)
        del ctr

        return (((mm_pixels_ratio ** 2 )* pixel_counts)/100 )
 
        
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
 

 
    def bounding_box_get_pixel_difference(self, vis, bounding_box, ctr):
        #Detecting the length of bounding box to get the correct ratio

        ctr.change_field_of_view(step=-9)
      
                
        vis.get_render_option().point_size = 5
        red_box_image = vis.capture_screen_float_buffer(True)
        red_box_width_mm = bounding_box.get_extent()[0]

        red_box_image_array = np.multiply(np.array(red_box_image), 255).astype(np.uint8)
        red_box_mid_y = red_box_image_array.shape[0]

        red_box_middle_row = red_box_image_array[int(red_box_mid_y/2)]
        red_box_middle_row_red_locations = ~((red_box_middle_row[:,0] == 255) & (red_box_middle_row[:,1] == 255)  & (red_box_middle_row[:,2] == 255))

        red_box_red_locations = np.where(red_box_middle_row_red_locations)[0]
        #Here we get the pixel to cm ratio
        pixels_difference = (red_box_red_locations[2] - red_box_red_locations[1] ) #* 0.9
        del ctr
        return red_box_width_mm, pixels_difference