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
        mm_squared = (ceremic_pixel * (mm_per_pixel * mm_per_pixel)) 
        # mm to cm
        cm_squared = mm_squared / 100 
        return cm_squared
        
 
    def get_mask_pixel_width(self, image):
        #Turned the color_grid mask into numpy array
        np_array = (np.array(image))
    
        x_coordiantes_mask = (sorted(np.where(np_array>200)[1]))
        return x_coordiantes_mask[-15] - x_coordiantes_mask[5]


    def get_2d_area(self, _2d_picture_path, masked_ceremics = None, mask_grid = None):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        try:
            if not (masked_ceremics and  mask_grid):
                image = main_model.open_image(_2d_picture_path)
            
                mask_grid = main_presenter.colorgrid_predictor.predict(image)
                masked_ceremics = main_presenter.ceremic_predictor.predict(image) 
            mm_per_pixel =  53.98 /self.get_mask_pixel_width(mask_grid)  #53.98 is the width of the credit-card size color grid
            tif_area =  self.get_ceremic_area(masked_ceremics, mm_per_pixel)
        except:
            tif_area = 1 
        return tif_area
    
    def get_2d_width_length(self,path_2d , masked_ceremics = None, mask_grid = None):

        main_model, main_view, main_presenter = self.get_model_view_presenter()

        if not (masked_ceremics and mask_grid):
            image = main_model.open_image(path_2d)
            masked_ceremics = main_presenter.ceremic_predictor.predict(image)
            mask_grid = main_presenter.colorgrid_predictor.predict(image)
        masked_ceremics_bool = (((np.array(masked_ceremics)).astype(bool)))

        mm_per_pixel =  53.98 /self.get_mask_pixel_width(mask_grid)  #53.98 is the width of the credit-card size color grid
        indices = (np.nonzero(masked_ceremics_bool))
  

        y_diff =  abs(max(indices[0]) - min(indices[0])) * mm_per_pixel
        x_diff = abs(max(indices[1]) - min(indices[1])) * mm_per_pixel 
        width = min(y_diff, x_diff)
        length = max(y_diff,x_diff)
        return width , length 
 

    def get_contour_2d(self, img_path):
        import numpy as np
        import open3d as o3d
        from PIL import Image
        import cv2

        main_model, main_view, main_presenter = self.get_model_view_presenter()

        image = Image.open(img_path).resize((450, 300), Image.ANTIALIAS)

        masked_ceremics = main_presenter.ceremic_predictor.predict(image)

        masked_ravel = np.array(masked_ceremics)
        masked_ravel[masked_ravel < 180] = 0

        masked_ravel[masked_ravel != 0] = 255

        pil_image = Image.fromarray(masked_ravel).convert("RGB")

        open_cv_image = np.array(pil_image)
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        img_gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

        ret, thresh = cv2.threshold(img_gray, 127, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, 2, 1)
        cnt2 = contours[0]
        return cnt2