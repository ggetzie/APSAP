import numpy as np
import cv2

from .segmentation import MaskPredictor, InvalidMaskType


def get_mm_per_pixel(image, color_grid_predictor: MaskPredictor):
    """This function gets the the ratio between 1 mm in real life and 1 pixel

    Args:
        image (pillow image): The pillow image of the picture we want to measure

    Returns:
        double: the ratio between 1 mm in real life and 1 pixel
    """
    if color_grid_predictor.mask_type == "colorgrid":
        mm_difference_x = 50.8
    elif color_grid_predictor.mask_type == "colorgrid_24":
        mm_difference_x = 53.98
    else:
        raise InvalidMaskType(
            f"Called get_mm_per_pixel with MaskPredictor of type {color_grid_predictor.mask_type}. Must be 'colorgrid' or 'colorgrid_24'."
        )

    # The predicted pixels of the color grid in the image, 0 means 0% chance the
    # pixel is color grid 255 means 100%, we take 200 as a threshold

    color_grid_pixels = np.array(color_grid_predictor.predict(image))

    # We get all the x coordinates of the color grid pixels and sort them
    x_coordinates_mask = sorted(np.where(color_grid_pixels > 200)[1])

    # We get the distance of the color grid in pixel
    pixel_difference_x = x_coordinates_mask[-15] - x_coordinates_mask[5]

    # We get the distance of the color grid in actual millimeters
    # (we can google the value)
    return mm_difference_x / pixel_difference_x
