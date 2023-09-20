import cv2


class CalculateIndividualSimilaritiesMixin:  # bridging the view(gui) and the model(data)
    def get_similarity_two_nums(self, a, b):  # a, b >
        """A similarity score between two numbers, 0 means exactly the same, 1 means infinitely different
        A small number is added to the denominator to avoid divided by 0.

        Returns:
            double: a double value that represents how close two numbers are
        """

        return abs(a - b) / (a + b + 0.0000000001)

    def get_area_similarity(self, area_3d, area_front, area_back):
        """_summary_

        Args:
            area_3d (double): _description_
            area_front (double): _description_
            area_back (double): _description_

        Returns:
            double: A similarity score representing how similiar the 3d model and the find are.
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        smaller_area = min(area_front, area_back)
        larger_area = max(area_front, area_back)

        return min(
            main_presenter.get_similarity_two_nums(larger_area, area_3d),
            main_presenter.get_similarity_two_nums(smaller_area, area_3d),
        )

    def get_width_length_similarity(
        self,
        width_3d,
        length_3d,
        width_front,
        length_front,
        width_back,
        length_back,
    ):
        """This function calculuates the similarity between a 3d model and the find by comparing the similarities of the width and the length of the bounding box.

        Args:
            width_3d (double): The width of the bounding box of the picture of the 3d model
            length_3d (double): The length of the bounding box of the picture of the 3d model
            width_front (double): The width of the bounding box of the picture of the front image
            length_front (double): The length of the bounding box of the picture of the front image
            width_back (double): The width of the bounding box of the picture of the back image
            length_back (double):  The length of the bounding box of the picture of the back image

        Returns:
            double: A similarity score representing how similiar the 3d model and the find are.
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        similarity_with_img_1 = main_presenter.get_similarity_two_nums(
            length_front, length_3d
        ) + main_presenter.get_similarity_two_nums(width_front, width_3d)

        similarity_with_img_2 = main_presenter.get_similarity_two_nums(
            length_back, length_3d
        ) + main_presenter.get_similarity_two_nums(width_back, width_3d)

        return min(similarity_with_img_1, similarity_with_img_2)

    def get_contour_simlarity(self, contour_3d, contour_front, contour_back):
        """This function calculates the similarity regarding 3d contour and contours of the images

        Args:
            contour_3d (object): A contour of the 3d model described the 3d model
            contour_front (object): A contour of the 3d model described the front image
            contour_back (object): A contour of the 3d model described the back image

        Returns:
            double: A similarity score representing how similiar the 3d model and the find are.
        """
        closeness_1 = cv2.matchShapes(contour_front, contour_3d, 1, 0.0)
        closeness_2 = cv2.matchShapes(contour_back, contour_3d, 1, 0.0)
        sim = min(closeness_1, closeness_2)
        return sim
