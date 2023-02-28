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

        self.ceremic_predictor = MaskPredictor("./computation/ceremicsmask.pt")
        self.colorgrid_predictor = MaskPredictor("./computation/colorgridmask.pt")
 
        img = model.open_image("assets/reference_placeholder.png", full_size=False).convert('RGB')

        self.ceremic_predictor.predict(img)
       # self.colorgrid_predictor.predict(img)
    def measure_pixels_2d(self, img_1_path, img_2_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        #Here let's get the ceremic and color grid here at once, that takes
        image_1 = main_model.open_image(img_1_path, full_size=False)

        masked_ceremics_1 = main_presenter.ceremic_predictor.predict(image_1)
        mask_grid_1 = main_presenter.colorgrid_predictor.predict(image_1)

        image_2 = main_model.open_image(img_2_path, full_size=False)
        masked_ceremics_2 = main_presenter.ceremic_predictor.predict(image_2)
        mask_grid_2 = main_presenter.colorgrid_predictor.predict(image_2)

        area_img_1 = main_presenter.get_2d_area(img_1_path, masked_ceremics_1, mask_grid_1)
        area_img_2 = main_presenter.get_2d_area(img_2_path,  masked_ceremics_2, mask_grid_2)
       
        # Brightness based simliarity
   
        light_ima_1 = main_presenter.get_2d_light_summary(img_1_path, masked_ceremics_1 )
        light_ima_2 = main_presenter.get_2d_light_summary(img_2_path, masked_ceremics_2)
        

        # Fourth one, width length
      
        img_1_width_length = main_presenter.get_2d_width_length(img_1_path, masked_ceremics_1, mask_grid_1)
        img_2_width_length = main_presenter.get_2d_width_length(img_2_path,  masked_ceremics_2, mask_grid_2)
    
      


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
        _3d_color = main_view.colors_3d[i]
        width_length_3d = main_view.width_lengths_3d[i][0]

        color_brightness_3d = main_view.brightnesses_3d[i][0][3]
        color_brightness_std_3d = main_view.brightnesses_3d[i][0][-1]
   

        return (
            _3d_area,
            _3d_color,
            0,
            width_length_3d,
            color_brightness_3d,
            color_brightness_std_3d,
            batch_num,
            piece_num,
        )
