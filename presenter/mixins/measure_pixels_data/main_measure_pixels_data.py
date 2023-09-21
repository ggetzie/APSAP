import sys
import time
import re
import diskcache
sys.path.insert(0, "../../..")
from computation.nn_segmentation import MaskPredictor
from .measure_2d import Measure2DMixin
from .measure_3d import Measure3dMixin
from PyQt5.QtCore import QCoreApplication


class MeasurePixelsDataMixin(Measure2DMixin, Measure3dMixin):
    def __init__(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        main_presenter.ceremic_predictor = MaskPredictor(
            r".\computation\ceremicsmask.pt"
        )
        main_presenter.colorgrid_predictor = MaskPredictor(
            r".\computation\colorgridmask.pt"
        )
        main_presenter.ceremic_predictor.predict(
            main_model.open_image(main_model.reference_place_holder_img) 
        )

    # self.colorgrid_predictor.predict(img)
    def measure_pixels_2d(self, path_front, path_back):
        try:
            main_model, main_view, main_presenter = self.get_model_view_presenter()

            (
                area_front,
                width_front,
                length_front,
                contour_front,
            ) = main_presenter.get_area_width_length_contour2d(path_front)

            (
                area_back,
                width_back,
                length_back,
                contour_back,
            ) = main_presenter.get_area_width_length_contour2d(path_back)

        except:
            print("Ooops we are doing that")
            (
                area_front,
                width_front,
                length_front,
                contour_front,
            ) = (
                1,
                1,
                1,
                main_presenter.get_contour_2d(main_model.reference_place_holder_img),
            )
            (
                area_back,
                width_back,
                length_back,
                contour_back,
            ) = (
                1,
                1,
                1,
                main_presenter.get_contour_2d(main_model.reference_place_holder_img),
            )

        return (
            (area_front, width_front, length_front, contour_front),
            (area_back,  width_back, length_back, contour_back)
        )

    def measure_pixels_3d(self, path_3d):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        cache_result = main_model.cache_3d.get(path_3d)
        ( year,
            batch,
            piece) = main_presenter.get_year_batch_piece(path_3d)
        if cache_result and (type(cache_result) is tuple) and len(cache_result) == 6:
            print(f"Loading {path_3d} directly from library")
            return (cache_result)
         
        print(f"Measuring 3d model: {path_3d} ")
        # Extra the batch and piece number from the path

        main_view.statusLabel.setText(f"Measuring 3d model {path_3d}")
        main_view.statusLabel.repaint()
        QCoreApplication.processEvents()
    

        (
            area_3d,
            width_length_3d,
        ) = main_presenter.get_3d_object_area_and_width_length(path_3d)

        contour_3d = main_presenter.get_contour_3d(path_3d)

        return_values = (
            area_3d,
            width_length_3d,
            contour_3d, 
            year,
            batch,
            piece,
        )

        main_model.cache_3d.set(path_3d, return_values)

        return return_values
