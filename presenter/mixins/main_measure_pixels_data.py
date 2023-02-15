from  computation.nn_segmentation import MaskPredictor
from scipy.ndimage import binary_dilation
from PIL import Image
import open3d as o3d 
import numpy as np
import smallestenclosingcircle
from presenter.mixins.measure_pixels_data.measure_2d_pixels_data import MeasurePixels2DDataMixin
from presenter.mixins.measure_pixels_data.measure_3d_pixels_data import MeasurePixels3DDataMixin


 

class MeasurePixelsDataMixin(MeasurePixels2DDataMixin, MeasurePixels3DDataMixin):  # bridging the view(gui) and the model(data)
    def __init__(self, view, model):
     
        self.ceremic_predictor = MaskPredictor("./computation/ceremicsmask.pt")
        self.colorgrid_predictor = MaskPredictor("./computation/colorgridmask.pt")
    
    def get_pixels_measuring_results__2d(self, _2d_image_path_image_1, _2d_image_path_image_2):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        _2d_area_image_1 = main_presenter.get_2d_picture_area(_2d_image_path_image_1)
        _2d_area_image_2 = main_presenter.get_2d_picture_area(_2d_image_path_image_2)

        # Brightness based simliarity
        color_brightness_2d_image_1 = main_presenter.get_brightness_summary_from_2d(
            _2d_image_path_image_1
        )

        color_brightness_2d_image_2 = main_presenter.get_brightness_summary_from_2d(
            _2d_image_path_image_2
        )

   

        # Fourth one, width length
        _2d_width_length_image_1 = main_presenter.get_2d_width_length(
            _2d_image_path_image_1
        )
        _2d_width_length_image_2 = main_presenter.get_2d_width_length(
            _2d_image_path_image_2
        )
        # Getting the simlarity scores here
        _2d_area_circle_ratio_image_1 = main_presenter.get_2d_area_circle_ratio(
            _2d_image_path_image_1
        )
        _2d_area_circle_ratio_image_2 = main_presenter.get_2d_area_circle_ratio(
            _2d_image_path_image_2
        )

        return _2d_area_image_1,  _2d_area_image_2, color_brightness_2d_image_1, color_brightness_2d_image_2, _2d_width_length_image_1, _2d_width_length_image_2, _2d_area_circle_ratio_image_1,  _2d_area_circle_ratio_image_2

    def get_pixels_measuring_results__3d(self, i):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        
        _3d_area = main_view.all_3d_areas[i][0]
        batch_num = main_view.all_3d_areas[i][1]
        piece_num = main_view.all_3d_areas[i][2]
        _3d_color = main_view.all_3d_colors_summaries[i]
        width_length_3d = main_view.all_3d_width_length_summaries[i][0]

        color_brightness_3d = main_view.all_3d_brightness_summaries[i][0][3]
        color_brightness_std_3d = main_view.all_3d_brightness_summaries[i][0][-1]
        all_3d_area_circle_ratio = main_view.all_3d_area_circle_ratios[i][0]

        return _3d_area, _3d_color, all_3d_area_circle_ratio, width_length_3d, color_brightness_3d, color_brightness_std_3d, batch_num, piece_num
