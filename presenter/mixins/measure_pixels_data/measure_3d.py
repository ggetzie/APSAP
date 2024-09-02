from PIL import Image
import open3d as o3d
import numpy as np
import cv2


class Measure3dMixin:  # bridging the view(gui) and the model(data)

    def get_area_width_length_contour3d(self, path_3d):
        """The function gets the area, width, length and the contour of the 3d model

        Args:
            path_3d (str): The path to the 3d model

        Returns:
            (area, width, length, contour): The four measured values of the 3d model
        """
        _, main_view, main_presenter = self.get_model_view_presenter()
        # Get the window to which we put the loaded model to it so we can take picture
        # and measure the pixels
        ply_window = main_view.ply_window

        # Initializing the ply_window properly
        ply_window.get_render_option().point_size = 5
        ctr = ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)

        # Load the 3d model, and the bounding box of the 3d model
        current_pcd_load = o3d.io.read_point_cloud(path_3d)
        bounding_box = current_pcd_load.get_axis_aligned_bounding_box()
        bounding_box.color = (1, 0, 0)

        # Add the bounding box the the window
        ply_window.add_geometry(bounding_box)

        # Get the width and length of the bounding box, which is the width and length
        # of the 3d model
        (width_3d, length_3d) = main_presenter.get_width_length_3d(bounding_box)

        # Get the ratio between one mm and one pixel
        mm_pixels_ratio = main_presenter.get_mm_pixels_ratio(bounding_box, ply_window)
        ply_window.remove_geometry(bounding_box)

        # Load the 3d model of the sherd
        ply_window.add_geometry(current_pcd_load)

        # Get the area and contour of the 3d model.
        (area_3d) = main_presenter.get_area_3d(ply_window, mm_pixels_ratio)
        (contour3d) = main_presenter.get_contour_3d(ply_window)

        # Remove the 3d model from the window
        ply_window.remove_geometry(current_pcd_load)

        # Delete the control
        del ctr

        # Return the measured values
        return (area_3d, width_3d, length_3d, contour3d)

    def get_width_length_3d(self, bounding_box):
        """This function returns the width and length of the bounding box, an Open3d object

        Args:
            bounding_box (Object): An open3d object

        Returns:
            (width, length): The width and length of the bounding box,
            width is the shorter side, length is the longer side.
        """
        extents = bounding_box.get_extent()
        width_3d = min(extents[0], extents[1])
        length_3d = max(extents[0], extents[1])
        return (width_3d, length_3d)

    def get_mm_pixels_ratio(self, bounding_box, ply_window):
        """This function gets the the ratio between 1 mm in real life and 1 pixel.
        What it does is simple. It first creates a red bounding box. We then have the
        difference between two sides of the bounding box in mm, then we measure the
        difference between the two sides of the bounding box in pixels by taking a
        picture of it in the ply_window and analyze the pixels.

        Because we know how far 1 mm is in real life and 1 pixel is in the picture
        we can get their ratio

        Args:
            bounding_box (pillow image): The red bounding box indicates the pixel
            difference between the left

            ply_window(object): The window to which the 3d model is added
        Returns:
            double: the ratio between 1 mm in real life and 1 pixel
        """
        # Reset the ply window
        ply_window.get_render_option().point_size = 5
        ctr = ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)

        # Taking a picture from the ply window and normalize the pixels.
        red_box_image = ply_window.capture_screen_float_buffer(True)
        red_box_image_array = np.multiply(np.array(red_box_image), 255).astype(np.uint8)

        # The picture above has white and red pixels.
        # The red pixels are the where the bounding box of the 3d model is, white pixels
        # are the background

        # Here we get the center row of the picture from the y axis, so we have a list of
        # white(for the most part) values and red values
        red_box_middle_row = red_box_image_array[int(red_box_image_array.shape[0] / 2)]

        # We get a list of boolean values to indicate where the red pixels are.
        red_box_middle_row_red_locations = ~(
            (red_box_middle_row[:, 0] == 255)
            & (red_box_middle_row[:, 1] == 255)
            & (red_box_middle_row[:, 2] == 255)
        )

        # We get all the x coordinates of all the red values(aka bounding box)
        red_box_red_locations = np.where(red_box_middle_row_red_locations)[0]

        # We get the bounding box's pixels difference between the two side of the red bounding
        # box, so we can know the pixel differences between the left most and right most of
        # the bounding box

        if len(red_box_red_locations) >= 4:
            bounding_box_pixels_difference = (
                red_box_red_locations[2] - red_box_red_locations[1]
            )
        else:
            bounding_box_pixels_difference = (
                red_box_red_locations[1] - red_box_red_locations[0]
            )

        # The bounding box width in actual dimension in real life can be get using get_extent()[0]
        bounding_box_width_mm = bounding_box.get_extent()[0]

        # We return the ratio
        return bounding_box_width_mm / bounding_box_pixels_difference

    def get_area_3d(self, ply_window, mm_pixels_ratio):
        """This function gets the area of the ceramics in the ply window by counting
        the number of pixels from the picture taken in the ply_window and scale with
        the proper mm_pixels_ratio

        Args:
            ply_window(object): The window to which the 3d model is added
            mm_pixels_ratio (double):  the ratio between 1 mm in real life and 1 pixel

        Returns:
            double: The area of the ceramics
        """
        # Resetting the ply_window
        ply_window.get_render_option().point_size = 5
        ctr = ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)

        # Taking a picture of the ply_window
        object_image = ply_window.capture_screen_float_buffer(True)

        # Counting the number of pixels where the pixels are not white,
        # thus the number of pixels representing the sherd
        object_image_array = (
            np.multiply(np.array(object_image), 255).astype(np.uint8).reshape(-1, 3)
        )
        object_image_array_object_locations = ~(
            (object_image_array == (255, 255, 255)).all(axis=-1)
        )
        pixel_counts = np.count_nonzero(object_image_array_object_locations)

        # Get the area of the 3d model
        area_3d = ((mm_pixels_ratio**2) * pixel_counts) / 100
        return area_3d

    def get_contour_3d(self, ply_window):
        """This function gets the contour of the 3d model

        Args:
            ply_window (object): the ply window of the point cloud

        Returns:
            object: A structure in opencv that describe a contour
        """
        # Resetting the ply window
        ply_window.get_render_option().point_size = 5
        ctr = ply_window.get_view_control()
        ctr.change_field_of_view(step=-9)

        # Get the picture from the ply_window
        object_image = ply_window.capture_screen_float_buffer(True)

        # Turn the image into black and white
        pic = np.array(
            Image.fromarray(
                np.multiply(np.array(object_image), 255).astype(np.uint8)
            ).convert("L")
        )

        # Since white means background, black means ceramics for picture taken in ply_window,
        # we have to flip the value so that background is black, ceramic area is white.
        pic[pic == 255] = 0
        pic[pic != 0] = 255

        # Filter the opencv image
        _, thresh = cv2.threshold(pic, 127, 255, 0)
        # Get the first contour detected
        contours, _ = cv2.findContours(thresh, 2, 1)
        contour3d = contours[0]
        return contour3d
