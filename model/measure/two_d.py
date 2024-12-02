import numpy as np
from PIL import Image
import cv2

from .segmentation import MaskPredictor, InvalidMaskType


def get_mm_per_pixel(image: Image.Image, color_grid_predictor: MaskPredictor):
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


def get_ceramic_mask(image: Image.Image, ceramic_predictor: MaskPredictor):
    """This functions open an image in 450 x 300.

    Args:
        image (PIL.Image.Image): A PIL image object to extract the ceramic mask from

    Returns:
        Pillow Image: A PIL image object containing the ceramic mask
    """
    return ceramic_predictor.predict(image)


def get_contour(ceramic_mask: Image.Image):
    _, thresh = cv2.threshold(np.array(ceramic_mask), 127, 255, 0)
    contours, _ = cv2.findContours(thresh, 2, 1)
    return contours[0]


def get_ceramic_width_length(ceramic_mask: np.ndarray, mm_per_pixel: float):
    """This function gets the width and length of the ceramic in mm

    Args:
        ceramic_mask (np.ndarray): The mask of the ceramic
        mm_per_pixel (float): The ratio between 1 mm in real life and 1 pixel

    Returns:
        tuple: The width and length of the ceramic in mm
    """
    # old method
    # ceramic_mask_bool = (np.array(ceramic_mask)).astype(bool)
    # indices = np.nonzero(ceramic_mask_bool)
    # y_diff = abs(max(indices[0]) - min(indices[0])) * mm_per_pixel
    # x_diff = abs(max(indices[1]) - min(indices[1])) * mm_per_pixel
    # width = min(y_diff, x_diff)
    # length = max(y_diff, x_diff)

    contour = get_contour(ceramic_mask)
    _, _, bb_w, bb_h = cv2.boundingRect(contour)
    # convert to mm
    bb_w_mm = bb_w * mm_per_pixel
    bb_h_mm = bb_h * mm_per_pixel
    # width is the short side, length is the long side
    width = min(bb_w_mm, bb_h_mm)
    length = max(bb_w_mm, bb_h_mm)
    return width, length


def get_ceramic_area(ceramic_mask: Image.Image, mm_per_pixel: float) -> float:
    """This function gets the area of the ceramic in mm^2

    Args:
        ceramic_mask (np.ndarray): The mask of the ceramic
        mm_per_pixel (float): The ratio between 1 mm in real life and 1 pixel

    Returns:
        double: The area of the ceramic in mm^2
    """
    ceramic_mask_bool = (np.array(ceramic_mask)).astype(bool)
    area_mm2 = np.sum(ceramic_mask_bool) * mm_per_pixel**2
    area_cm2 = area_mm2 / 100
    return area_cm2


def get_masked_image(image: Image.Image, mask: Image.Image):
    return Image.composite(image, Image.new("RGB", image.size, (255, 255, 255)), mask)
