import numpy as np
import cv2


class Measure2DMixin:  # bridging the view(gui) and the model(data)

    def get_area_width_length_contour2d(self, path):
        """Get the measured values of area, width, length and contour of the image in the given path

        Args:
            path (str): The path to the location of the image

        Returns:
            tuple: All the measured values
        """
        main_model, _, main_presenter = self.get_model_view_presenter()
        image = main_model.open_image(path)

        # The predicted pixels of the ceramic
        ceramic_mask = main_presenter.ceramic_predictor.predict(image)

        # The ratio between 1 mm in real life and 1 pixel in the picture
        mm_per_pixel = self.get_mm_per_pixel(image)

        (area) = self.get_ceramic_area(ceramic_mask, mm_per_pixel)
        (width, length) = self.get_ceramic_width_length(ceramic_mask, mm_per_pixel)
        (contour2d) = self.get_contour_2d(path, ceramic_mask)

        return (area, width, length, contour2d)

    def get_mm_per_pixel(self, image):
        """This function gets the the ratio between 1 mm in real life and 1 pixel

        Args:
            image (pillow image): The pillow image of the picture we want to measure

        Returns:
            double: the ratio between 1 mm in real life and 1 pixel
        """
        _, main_view, main_presenter = self.get_model_view_presenter()

        # The predicted pixels of the color grid in the image, 0 means 0% chance the
        # pixel is color grid 255 means 100%, we take 200 as a threshold

        if main_view.comboBox.currentText() != "24ColorCard":
            color_grid_pixels = np.array(
                main_presenter.colorgrid_predictor.predict(image)
            )
        else:
            color_grid_pixels = np.array(
                main_presenter.colorgrid_predictor_24color.predict(image)
            )

        # We get all the x coordinates of the color grid pixels and sort them
        x_coordinates_mask = sorted(np.where(color_grid_pixels > 200)[1])

        # We get the distance of the color grid in pixel
        pixel_difference_x = x_coordinates_mask[-15] - x_coordinates_mask[5]

        # We get the distance of the color grid in actual millimeters(we can google the value)
        if main_view.comboBox.currentText() != "24ColorCard":
            mm_difference_x = 53.98
        else:
            mm_difference_x = 50.8

        return mm_difference_x / pixel_difference_x

    def get_ceramic_area(self, ceramic_mask, mm_per_pixel):
        """This function calculates the actual area of the ceramics by scaling
        the number of pixels with the mm-pixel ratio

        Args:
            ceramic_mask (Tensor): Predicted pixel locations of the ceramic.
            mm_per_pixel (double): The ratio between 1 mm and 1 pixel

        Returns:
            double: The calculated area
        """
        _, _, _ = self.get_model_view_presenter()

        # Count the number of ceramic pixels
        number_of_ceramic_pixels = np.count_nonzero(np.array(ceramic_mask) >= 170)

        # Get the actual area of the ceramics in mm
        area_mm_squared = number_of_ceramic_pixels * (mm_per_pixel * mm_per_pixel)

        # Get the actual area of the ceramics in cm
        area_cm_squared = area_mm_squared / 100
        return area_cm_squared

    def get_ceramic_width_length(self, ceramic_mask, mm_per_pixel):
        """Get the width and length of the bounding rectangle of the ceramics.

        Args:
            ceramic_mask (Tensor): Predicted pixel locations of the ceramic.
            mm_per_pixel (double): The ratio between 1 mm and 1 pixel

        Returns:
            (double, double): The width and length of the rectangle surrounding of the ceramics.
        """
        _, _, _ = self.get_model_view_presenter()

        # Simply filtering the ceramic mask, so that ceramic pixels are true,
        # non-ceramic pixels are false
        masked_ceramics_bool = (np.array(ceramic_mask)).astype(bool)

        # Get the x and y coordinates of the ceramics pixels
        indices = np.nonzero(masked_ceramics_bool)

        # Calculate the distance in the x direction in mm
        y_diff = abs(max(indices[0]) - min(indices[0])) * mm_per_pixel
        # Calculate the distance in the y direction in mm
        x_diff = abs(max(indices[1]) - min(indices[1])) * mm_per_pixel

        # width is the shorter side, length is the longer side
        width = min(y_diff, x_diff)
        length = max(y_diff, x_diff)
        return width, length

    def get_contour_2d(self, img_path, ceramic_mask=None):
        """Calculate the contour of the image in opencv

        Returns:
            object: A complex opencv structure describing the contour of the ceramics
        """

        main_model, _, main_presenter = self.get_model_view_presenter()

        # if the ceramic_mask is not predicted already, we predict it ourselves
        if not ceramic_mask:
            image = main_model.open_image(img_path)
            ceramic_mask = main_presenter.ceramic_predictor.predict(image)

        # We surpass the value of the values of the pixels with the range
        _, thresh = cv2.threshold(np.array(ceramic_mask), 127, 255, 0)

        # Calculate the contour
        contours, _ = cv2.findContours(thresh, 2, 1)

        # We only care about the first contour
        contour2d = contours[0]
        return contour2d
