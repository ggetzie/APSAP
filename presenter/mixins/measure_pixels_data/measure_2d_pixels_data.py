from  computation.nn_segmentation import MaskPredictor
from scipy.ndimage import binary_dilation
from PIL import Image
import open3d as o3d 
import numpy as np
import smallestenclosingcircle
 

 

class MeasurePixels2DDataMixin:  # bridging the view(gui) and the model(data)

    def get_ceremic_area(self, ceremic_mask, mm_per_pixel):
        #Turn the mask to an array
        ceremic_array = (np.array(ceremic_mask))
        ceremic_pixel = (np.count_nonzero((ceremic_array >=170)))
        # Turn number of pixels(aka pixel area) into area in mm
        mm_squared = (ceremic_pixel * (mm_per_pixel* mm_per_pixel)) 
        # mm to cm
        cm_squared = mm_squared / 100 
        return cm_squared
        
    def get_2d_area_circle_ratio(self, _2d_object_path) -> float:
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        area_in_pixels= main_presenter.get_2d_area_by_pixels(_2d_object_path, main_presenter.ceremic_predictor)
        circle_in_pixels = main_presenter.get_2d_enclosing_circle_area(_2d_object_path, main_presenter.ceremic_predictor)
        return area_in_pixels/circle_in_pixels

    def get_mask_pixel_width(self, image):
        #Turned the color_grid mask into numpy array
        np_array = (np.array(image))
    
        x_coordiantes_mask = (sorted(np.where(np_array>200)[1]))
        return x_coordiantes_mask[-15] - x_coordiantes_mask[5]


    def get_2d_picture_area(self, _2d_picture_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        image = main_model.open_image(_2d_picture_path, full_size=False)
        
        mask_image = main_presenter.colorgrid_predictor.predict(image)
        mm_per_pixel =  53.98 /self.get_mask_pixel_width(mask_image)  #53.98 is the width of the credit-card size color grid
        ceremic_mask = main_presenter.ceremic_predictor.predict(image) 
        tif_area =  self.get_ceremic_area(ceremic_mask, mm_per_pixel)
        return tif_area
    
    def get_2d_width_length(self,path_2d):

        main_model, main_view, main_presenter = self.get_model_view_presenter()

    
        image = main_model.open_image(path_2d,full_size=False)
        masked_ceremics = main_presenter.ceremic_predictor.predict(image)
        masked_ceremics_bool = (((np.array(masked_ceremics)).astype(bool)))
        mask_grid = main_presenter.colorgrid_predictor.predict(image)
        mm_per_pixel =  53.98 /self.get_mask_pixel_width(mask_grid)  #53.98 is the width of the credit-card size color grid
        indices = (np.nonzero(masked_ceremics_bool))
        sorted_y_indices = sorted(indices[0])
        sorted_x_indices = sorted(indices [1])
    
        y_diff =  abs(sorted_y_indices[-1] - sorted_y_indices[0]) * mm_per_pixel
        x_diff = abs(sorted_x_indices[-1] - sorted_x_indices[0] ) * mm_per_pixel 
        width = min(y_diff, x_diff)
        length = max(y_diff,x_diff)
        return width , length 
 


    def get_brightness_summary_from_2d(self, image_path):

        main_model, main_view, main_presenter = self.get_model_view_presenter()

        image = main_model.open_image(image_path,full_size=False)
        masked = main_presenter.ceremic_predictor.predict(image)
        
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
    
    def get_2d_area_by_pixels(self, image_path, predictor):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        image = main_model.open_image(image_path, full_size=False)
        mask = predictor.predict(image)
        mask_array = np.array(mask)
        pixels = np.nonzero(mask_array)
        pixel_area = len(pixels[0])
        return pixel_area

        
    def get_2d_enclosing_circle_area(self, image_path, predictor):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        image = main_model.open_image(image_path, full_size=False)
        mask = predictor.predict(image)
        mask_array = np.array(mask)
        #Here using a technique to leave out only the points of the object consisting of the boundary, so that we have much fewer points to handle
        k = np.ones((3,3),dtype=int)
        boundary_array = binary_dilation(mask_array==0, k) & mask_array
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
        return (radius**2 ) * 3.1416

    def get_color_summary_from_2d(self, image_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()



        image = main_model.open_image(image_path,full_size=False)
        masked = main_presenter.ceremic_predictor.predict(image)
        
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