import sys
import time
import re
import diskcache

sys.path.insert(0, "../../..")
from computation.nn_segmentation import MaskPredictor
from .measure_2d import Measure2DMixin
from .measure_3d import Measure3dMixin
from PyQt5.QtCore import QCoreApplication
import logging

class MeasurePixelsDataMixin(Measure2DMixin, Measure3dMixin):
    def __init__(self):
        """This constructor initializes the two Pytorch-trained neural networks used
        for measuring the pixels. It also runs the networks for once so it loads faster for
        subsequent runs
        """
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
        main_presenter.colorgrid_predictor.predict(
            main_model.open_image(main_model.reference_place_holder_img)
        )

    def measure_pixels_2d(self, path_front, path_back):
        """This function measures the front image and the back image and return
        the measured values. In case, it failed to measure, it return the default values.

        Args:
            path_front (str): Path to the front picture
            path_back (str): path to the back picture

        Returns:
            tuple: Tuple of the measured values
        """
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
            logging.error(f"We failed to measure for either the paths: {path_front} and {path_back}")
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
            (area_back, width_back, length_back, contour_back),
        )

    def measure_pixels_3d(self, path_3d):
        """This function measures the 3d model in the given path. In case it fails,
        it returns the fallback value.

        Args:
            path_3d (str): The path to the 3d model

        Returns:
            tuple:  Tuple of the measured values
        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        #Check if the result has already been cached. If yes, directly return the result
        cache_result = main_model.cache_3d.get(path_3d)
        if cache_result != None and len(cache_result) == 7:
            logging.info(f"Loading {path_3d} directly from library")
            return cache_result
        
        #In case it is not cached, we have to measure the pixels directly.
        #Get the year, batch and piece of the 3d model.
        (year, batch, piece) = main_presenter.get_year_batch_piece(path_3d)


        #Showing that we are measure the 3d models
        logging.info(f"Measuring 3d model: Year {year}, Batch: {batch}, Piece: {piece} ")
        main_view.statusLabel.setText(f"Measuring 3d model: Year {year}, Batch: {batch}, Piece: {piece} ")
        main_view.statusLabel.repaint()
        QCoreApplication.processEvents()



        #Try to get the measurements. If there is an error, return the value
        try:
            (
                area_3d,
                width_3d,
                length_3d,
                contour_3d,
            ) = main_presenter.get_area_width_length_contour3d(path_3d)

            return_values = (
                area_3d,
                width_3d,
                length_3d,
                contour_3d,
                year,
                batch,
                piece,
            )
            #Caching the calculuated values
            main_model.cache_3d.set(path_3d, return_values)
        except:
            logging.error(f"We failed to measure the pixels in {path_3d}")
            (
                area_3d,
                width_3d,
                length_3d,
                contour_3d,
            ) = (
                1,
                1,
                1,
                main_presenter.get_contour_2d(main_model.reference_place_holder_img)
            )

            return_values = (
                area_3d,
                width_3d,
                length_3d,
                contour_3d,
                year,
                batch,
                piece,
            )
        return return_values
