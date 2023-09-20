import sys
sys.path.insert(0, '../../..')
from computation.nn_segmentation import MaskPredictor
from scipy.ndimage import binary_dilation
from PIL import Image
import open3d as o3d
import numpy as np
import smallestenclosingcircle
from .measure_2d_pixels_data import (
    MeasurePixels2DDataMixin,
)
from .measure_3d_pixels_data import (
    MeasurePixels3DDataMixin,
)
import time

class MeasurePixelsDataMixin(
    MeasurePixels2DDataMixin, MeasurePixels3DDataMixin
):  
    def __init__(self, view, model):

        self.ceremic_predictor = MaskPredictor(r".\computation\ceremicsmask.pt")
        self.colorgrid_predictor = MaskPredictor(r".\computation\colorgridmask.pt")
 
        self.reference_place_holder_img = model.open_image("assets/reference_placeholder.png").convert('RGB')

        self.ceremic_predictor.predict(self.reference_place_holder_img)
       # self.colorgrid_predictor.predict(img)
    def measure_pixels_2d(self, path_front, path_back):
        try:
            main_model, main_view, main_presenter = self.get_model_view_presenter()

            #Here let's get the ceremic and color grid here at once, that takes
            image_1 = main_model.open_image(path_front)

            masked_ceremics_1 = main_presenter.ceremic_predictor.predict(image_1)
            mask_grid_1 = main_presenter.colorgrid_predictor.predict(image_1)

            image_2 = main_model.open_image(path_back)
            masked_ceremics_2 = main_presenter.ceremic_predictor.predict(image_2)
            mask_grid_2 = main_presenter.colorgrid_predictor.predict(image_2)

            #For now wrapping them in try and except, will fix later.
            #  
        
            area_img_1 = main_presenter.get_2d_area(path_front, masked_ceremics_1, mask_grid_1)
            area_img_2 = main_presenter.get_2d_area(path_back,  masked_ceremics_2, mask_grid_2)  
            img_1_width_length = main_presenter.get_2d_width_length(path_front, masked_ceremics_1, mask_grid_1)
            img_2_width_length = main_presenter.get_2d_width_length(path_back,  masked_ceremics_2, mask_grid_2)
            contour1_2d = main_presenter.get_contour_2d(path_front)
            contour2_2d = main_presenter.get_contour_2d(path_back)
        
        


        except:
            area_img_1 = 1
            area_img_2 = 1
            img_1_width_length = (1,1)
            img_2_width_length = (1,1)
            contour1_2d = main_presenter.get_contour_2d(main_presenter.reference_place_holder_img)
            contour2_2d = main_presenter.get_contour_2d(main_presenter.reference_place_holder_img)


        return (
            area_img_1,
            area_img_2,
            img_1_width_length,
            img_2_width_length,
            contour1_2d,
            contour2_2d
        )

 
    def measure_pixels_3d(self, path_3d):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        
        (batch_num, piece_num, width_length_summary, area,  context, contour, year) = self.load_ply_info_from_cache_or_calc(path_3d)
        
        _3d_area = area
        batch_num = batch_num
        piece_num = piece_num
        width_length_3d = width_length_summary
        contour_3d = contour
        return (
            _3d_area,
            width_length_3d,
            contour_3d,
            batch_num,
            piece_num,
            year
        )
