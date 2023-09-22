from  computation.nn_segmentation import MaskPredictor
from PIL import Image
import open3d as o3d 
import numpy as np
import smallestenclosingcircle
import cv2

 

class Measure2DMixin:  # bridging the view(gui) and the model(data)



        
    def get_area_width_length_contour2d(self, path):
        """Get the measured values of area, width, length and contour of the image in the given path

        Args:
            path (str): The path to the location of the image

        Returns:
            tuple: All the measured values
        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        image = main_model.open_image(path)

        #The predicted pixels of the ceremic
        ceremic_mask = main_presenter.ceremic_predictor.predict(image) 

        #The ratio between 1 mm in real life and 1 pixel in the picture
        mm_per_pixel  = self.get_mm_per_pixel(image)

        (area) = self.get_ceremic_area(ceremic_mask, mm_per_pixel)
        (width, length) = self.get_ceremic_width_length(ceremic_mask, mm_per_pixel)
        (contour2d) = self.get_contour_2d(path, ceremic_mask)

        return (area, width, length, contour2d)


    def get_mm_per_pixel(self, image):
        """This function gets the the ratio between 1 mm in real life and 1 pixel

        Args:
            image (pillow image): The pilow image of the picture we want to measure

        Returns:
            double: the ratio between 1 mm in real life and 1 pixel
        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        #The predicted pixels of the color grid in the image, 0 means 0% chance the pixel is color grid
        #255 means 100%, we take 200 as a threshhold
        color_grid_pixels = (np.array(main_presenter.colorgrid_predictor.predict(image)))

        #We get all the x coordinates of the color grid pixels and sort them
        x_coordiantes_mask = (sorted(np.where(color_grid_pixels>200)[1]))

        #We get the distance of the color grid in pixel
        pixel_difference_x = x_coordiantes_mask[-15] - x_coordiantes_mask[5]

        #We get the distance of the color grid in actual milimeters(we can google the value)
        mm_difference_x = 53.98
        return  (mm_difference_x/pixel_difference_x)
        
    def get_ceremic_area(self, ceremic_mask, mm_per_pixel):
        """This function calculuates the actual area of the ceremics by scaling the number of pixels with the mm-pixel ratio

        Args:
            ceremic_mask (Tensor): Predicted pixel locations of the ceremic.
            mm_per_pixel (double): The ratio between 1 mm and 1 pixel

        Returns:
            double: The calculated area
        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()

         
        #Count the number of ceremic pixels
        number_of_ceremic_pixels = np.count_nonzero(np.array(ceremic_mask) >=170)

        # Get the actual area of the ceremics in mm
        area_mm_squared = (number_of_ceremic_pixels * (mm_per_pixel * mm_per_pixel)) 

        # Get the actual area of the ceremics in cm
        area_cm_squared = area_mm_squared / 100 
        return area_cm_squared
        
    def get_ceremic_width_length(self, ceremic_mask, mm_per_pixel):
        """Get the width and length of the bounding rectangle of the ceremics.

        Args:
            ceremic_mask (Tensor): Predicted pixel locations of the ceremic.
            mm_per_pixel (double): The ratio between 1 mm and 1 pixel

        Returns:
            (double, double): The width and length of the rectangle surrounding of the ceremics.
        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        #Simply filtering the ceremic mask, so that ceremic pixels are true, non-cermic pixels are false
        masked_ceremics_bool = (np.array(ceremic_mask)).astype(bool)

        #Get the x and y coordinates of the ceremics pixels
        indices = (np.nonzero(masked_ceremics_bool))

        #Calculuate the distance in the x direction in mm
        y_diff =  abs(max(indices[0]) - min(indices[0])) * mm_per_pixel
        #Calculuate the distance in the y direction in mm
        x_diff = abs(max(indices[1]) - min(indices[1])) * mm_per_pixel 

        #width is the shorter side, length is the longer side
        width = min(y_diff, x_diff)
        length = max(y_diff,x_diff)
        return width , length 
 

 
    def get_contour_2d(self, img_path, ceremic_mask = None):

        """Calculuate the contour of the image in opencv

        Returns:
            object: A complex opencv structure describing the contour of the ceremics
        """        

        main_model, main_view, main_presenter = self.get_model_view_presenter()

        #if the ceremic_mask is not predicted already, we predict it ourselves
        if not ceremic_mask:
            image = main_model.open_image(img_path) 
            ceremic_mask = main_presenter.ceremic_predictor.predict(image)

        #We surpass the value of the values of the pixels with the range
        ret, thresh = cv2.threshold(np.array(ceremic_mask), 127, 255, 0)

        #Calculuate the contour
        contours, hierarchy = cv2.findContours(thresh, 2, 1)

        #We only care about the first contour
        contour2d = contours[0]
        return contour2d