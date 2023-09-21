from  computation.nn_segmentation import MaskPredictor
from scipy.ndimage import binary_dilation
from PIL import Image
import open3d as o3d 
import numpy as np
import smallestenclosingcircle
 

 

class Measure2DMixin:  # bridging the view(gui) and the model(data)


    def get_mm_per_pixel_and_masked_ceremics(self, path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        image = main_model.open_image(path)
        mask_grid = main_presenter.colorgrid_predictor.predict(image)
        ceremic_mask = main_presenter.ceremic_predictor.predict(image) 
        np_array = (np.array(mask_grid))
        x_coordiantes_mask = (sorted(np.where(np_array>200)[1]))
        pixel_difference =  x_coordiantes_mask[-15] - x_coordiantes_mask[5]
        mm_difference = 53.98
        return (ceremic_mask, (mm_difference/pixel_difference))
        
    def get_area_width_length_contour2d(self, path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        (ceremic_mask, mm_per_pixel ) = self.get_mm_per_pixel_and_masked_ceremics(path)
        area = self.get_ceremic_area(ceremic_mask, mm_per_pixel)
        (width, length) = self.get_ceremic_width_length(ceremic_mask, mm_per_pixel)
        contour2d = self.get_contour_2d(path, ceremic_mask)
        return (area, width, length, contour2d)
    def get_ceremic_area(self, ceremic_mask, mm_per_pixel):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        #Turn the mask to an array
        ceremic_array = (np.array(ceremic_mask))
        ceremic_pixel = (np.count_nonzero((ceremic_array >=170)))
        # Turn number of pixels(aka pixel area) into area in mm
        mm_squared = (ceremic_pixel * (mm_per_pixel * mm_per_pixel)) 
        # mm to cm
        area = mm_squared / 100 
        return area
        
    def get_ceremic_width_length(self, ceremic_mask, mm_per_pixel):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        masked_ceremics_bool = (((np.array(ceremic_mask)).astype(bool)))

        indices = (np.nonzero(masked_ceremics_bool))
        y_diff =  abs(max(indices[0]) - min(indices[0])) * mm_per_pixel
        x_diff = abs(max(indices[1]) - min(indices[1])) * mm_per_pixel 
        width = min(y_diff, x_diff)
        length = max(y_diff,x_diff)
        return width , length 
 

 
    def get_contour_2d(self, img_path, ceremic_mask = None):
        import numpy as np
        import open3d as o3d
        from PIL import Image
        import cv2

        main_model, main_view, main_presenter = self.get_model_view_presenter()

        if not ceremic_mask:
            image = main_model.open(img_path) 
            ceremic_mask = main_presenter.ceremic_predictor.predict(image)

        masked_ravel = np.array(ceremic_mask)
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