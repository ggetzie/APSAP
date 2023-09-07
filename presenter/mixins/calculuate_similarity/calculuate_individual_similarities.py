from PIL.ImageQt import ImageQt
from scipy.stats import gmean, tmean
import numpy as np
import cv2
import time
class CalculateIndividualSimilaritiesMixin:  # bridging the view(gui) and the model(data)
   
  

    def get_similarity_two_nums(self, a, b):  # a, b >

        # A new similiarity function
        return abs(a - b) / (
            a + b + 0.0000000001 # Add an extreme small amount to avoid divide by zero
        )  # If they are the same, it becomes zeros, if their difference approaches infinitry, it becomes 1.

    def get_area_similarity(self, _3d_area, _2d_area_1, _2d_area_2, a, b):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
       
      
        smaller_area = min(_2d_area_1, _2d_area_2)
        larger_area = max(_2d_area_1, _2d_area_2)

        # We only calculuate the similirity based upon the more simliar image in terms of the area regardless a and b.
        if main_presenter.get_similarity_two_nums(
            smaller_area, _3d_area
        ) > main_presenter.get_similarity_two_nums(larger_area, _3d_area):
            # We use a and b to get a more accurate similarity.
            
            return main_presenter.get_similarity_two_nums(larger_area * a + b, _3d_area)
        else:
            
            return main_presenter.get_similarity_two_nums(
                smaller_area * a + b, _3d_area
            )

    def get_brightness_similarity(
        self, _3d_brightness, _2d_brightness_1, _2d_brightness_2, a, b
    ):
        # Similiar reasoning behind function get_area_similarity()
        main_model, main_view, main_presenter = self.get_model_view_presenter()
 
        darker_brightness = min(_2d_brightness_1, _2d_brightness_2)
        brighter_brightness = max(_2d_brightness_1, _2d_brightness_2)

        if main_presenter.get_similarity_two_nums(
            darker_brightness, _3d_brightness
        ) > main_presenter.get_similarity_two_nums(brighter_brightness, _3d_brightness):
         

            return main_presenter.get_similarity_two_nums(
                brighter_brightness * a + b, _3d_brightness
            )
        else:
        
            return main_presenter.get_similarity_two_nums(
                darker_brightness * a + b, _3d_brightness
            )

    def get_brightness_std_similarity(
        self, _3d_brightness_std, _2d_brightness_std_1, _2d_brightness_std_2, a, b
    ):
        # Similiar reasoning behind function get_area_similarity()
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        smaller_brightness_std = min(_2d_brightness_std_1, _2d_brightness_std_2)
        larger_brightness_std = max(_2d_brightness_std_1, _2d_brightness_std_2)

        if main_presenter.get_similarity_two_nums(
            smaller_brightness_std, _3d_brightness_std
        ) > main_presenter.get_similarity_two_nums(
            larger_brightness_std, _3d_brightness_std
        ):
 
            return main_presenter.get_similarity_two_nums(
                larger_brightness_std * a + b, _3d_brightness_std
            )
        else:
             return main_presenter.get_similarity_two_nums(
                smaller_brightness_std * a + b, _3d_brightness_std
            )

    def get_width_length_similarity(
        self,
        _3d_pic_side_1,
        _3d_pic_side_2,
        _first_pic_side_1,
        _first_pic_side_2,
        _second_pic_side_1,
        _second_pic_side_2,
        a,
        b,
        c,
        d,
    ):
        # Similiar reasoning behind function get_area_similarity()
  
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        
        longer_side_3d = max(_3d_pic_side_1, _3d_pic_side_2)
        shorter_side_3d = min(_3d_pic_side_1, _3d_pic_side_2)

        longer_side_pic_1 = max(_first_pic_side_1, _first_pic_side_2)
        shorter_side_pic_1 = min(_first_pic_side_1, _first_pic_side_2)

        longer_side_pic_2 = max(_second_pic_side_1, _second_pic_side_2)
        shorter_side_pic_2 = min(_second_pic_side_1, _second_pic_side_2)

        # if without linear adjustment, the image is closer, the image is the one we pick. //For now, arithematic mean is used, other types of mean maybe considered later
        unadjusted_similarity_1 = (
            main_presenter.get_similarity_two_nums(longer_side_pic_1, longer_side_3d)
            + main_presenter.get_similarity_two_nums(
                shorter_side_pic_1, shorter_side_3d
            )
        ) / 2
        unadjusted_similarity_2 = (
            main_presenter.get_similarity_two_nums(longer_side_pic_2, longer_side_3d)
            + main_presenter.get_similarity_two_nums(
                shorter_side_pic_2, shorter_side_3d
            )
        ) / 2
        if unadjusted_similarity_1 > unadjusted_similarity_2:
            result = (
                main_presenter.get_similarity_two_nums(
                    shorter_side_pic_2 * a + b, shorter_side_3d
                )
            ) + main_presenter.get_similarity_two_nums(
                longer_side_pic_2 * c + d, longer_side_3d
            ) / 2
        else:
            result = (
                main_presenter.get_similarity_two_nums(
                    shorter_side_pic_1 * a + b, shorter_side_3d
                )
                + main_presenter.get_similarity_two_nums(
                    longer_side_pic_1 * c + d, longer_side_3d
                )
            ) / 2
        return result   

    def get_contour_simlarity(self, contour1_2d, contour2_2d, contour_3d):
            closeness_1 = cv2.matchShapes(contour1_2d,contour_3d,1,0.0)
            closeness_2 = cv2.matchShapes(contour2_2d,contour_3d,1,0.0)
            sim = min(closeness_1, closeness_2)
            return sim