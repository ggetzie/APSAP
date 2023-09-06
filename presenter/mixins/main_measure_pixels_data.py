from computation.nn_segmentation import MaskPredictor
from scipy.ndimage import binary_dilation
from PIL import Image
import open3d as o3d
import numpy as np
import smallestenclosingcircle
from presenter.mixins.measure_pixels_data.measure_2d_pixels_data import (
    MeasurePixels2DDataMixin,
)
from presenter.mixins.measure_pixels_data.measure_3d_pixels_data import (
    MeasurePixels3DDataMixin,
)
import time

class MeasurePixelsDataMixin(
    MeasurePixels2DDataMixin, MeasurePixels3DDataMixin
):  
    def __init__(self, view, model):

        self.ceremic_predictor = MaskPredictor(r".\computation\ceremicsmask.pt")
        self.colorgrid_predictor = MaskPredictor(r".\computation\colorgridmask.pt")
 
        img = model.open_image("assets/reference_placeholder.png", full_size=False).convert('RGB')

        self.ceremic_predictor.predict(img)
       # self.colorgrid_predictor.predict(img)
    def measure_pixels_2d(self, img_1_path, img_2_path):
        try:
            main_model, main_view, main_presenter = self.get_model_view_presenter()

            #Here let's get the ceremic and color grid here at once, that takes
            image_1 = main_model.open_image(img_1_path, full_size=False)

            masked_ceremics_1 = main_presenter.ceremic_predictor.predict(image_1)
            mask_grid_1 = main_presenter.colorgrid_predictor.predict(image_1)

            image_2 = main_model.open_image(img_2_path, full_size=False)
            masked_ceremics_2 = main_presenter.ceremic_predictor.predict(image_2)
            mask_grid_2 = main_presenter.colorgrid_predictor.predict(image_2)

            #For now wrapping them in try and except, will fix later.
            #  
        
            area_img_1 = main_presenter.get_2d_area(img_1_path, masked_ceremics_1, mask_grid_1)
            area_img_2 = main_presenter.get_2d_area(img_2_path,  masked_ceremics_2, mask_grid_2)
            light_ima_1 = main_presenter.get_2d_light_summary(img_1_path, masked_ceremics_1 )
            light_ima_2 = main_presenter.get_2d_light_summary(img_2_path, masked_ceremics_2)       
            img_1_width_length = main_presenter.get_2d_width_length(img_1_path, masked_ceremics_1, mask_grid_1)
            img_2_width_length = main_presenter.get_2d_width_length(img_2_path,  masked_ceremics_2, mask_grid_2)
            
        
        


        except:
            area_img_1 = 1
            area_img_2 = 1
            light_ima_1 = (1,1,1,1,1,1)
            light_ima_2 = (1,1,1,1,1,1)
            img_1_width_length = (1,1)
            img_2_width_length = (1,1)

        return (
            area_img_1,
            area_img_2,
            light_ima_1,
            light_ima_2,
            img_1_width_length,
            img_2_width_length,

        )


    def measure_pixels_3d(self, i):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        _3d_area = main_view.areas_3d[i][0]
        batch_num = main_view.areas_3d[i][1]
        piece_num = main_view.areas_3d[i][2]
        width_length_3d = main_view.width_lengths_3d[i][0]

        color_brightness_3d = main_view.brightnesses_3d[i][0][3]
        color_brightness_std_3d = main_view.brightnesses_3d[i][0][-1]
        contour_3d = main_view.contour_3d[i][0]

        return (
            _3d_area,
            
            0,
            width_length_3d,
            color_brightness_3d,
            color_brightness_std_3d,
            batch_num,
            piece_num,
            contour_3d
        )
    
    def measure_pixels_3d_new(self, path_3d):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        (batch_num, piece_num, brightness_3d, width_length_summary, area,   context, contour) = self.load_ply_info_from_cache_or_calc(path_3d)
        _3d_area = area
        batch_num = batch_num
        piece_num = piece_num
        width_length_3d = width_length_summary

        color_brightness_3d = brightness_3d[3]
        color_brightness_std_3d = brightness_3d[-1]
        contour_3d = contour
        return (
            _3d_area,
            
            0,
            width_length_3d,
            color_brightness_3d,
            color_brightness_std_3d,
            batch_num,
            piece_num,
            contour_3d
        )
