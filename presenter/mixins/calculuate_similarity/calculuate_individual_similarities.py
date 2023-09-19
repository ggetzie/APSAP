from PIL.ImageQt import ImageQt
from scipy.stats import gmean, tmean
import numpy as np
import cv2
import time
class CalculateIndividualSimilaritiesMixin:  # bridging the view(gui) and the model(data)
   
  

    def get_similarity_two_nums(self, a, b):  # a, b >

        """A similarity score between two numbers, 0 means exactly the same, 1 means infinitely different 
        A small number is added to the denominator to avoid divided by 0.

        Returns:
            double: a double value that represents how close two numbers are 
        """        

         
        return abs(a - b) / (
            a + b + 0.0000000001  
        )   

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

        return min(main_presenter.get_similarity_two_nums(larger_area, area_3d) , main_presenter.get_similarity_two_nums(
            smaller_area, area_3d
        ))
        
 

    def get_width_length_similarity(
        self,
        shorter_side_3d,
        longer_side_3d,
        shorter_side_pic_1,
        longer_side_pic_1,
        shorter_side_pic_2,
        longer_side_pic_2,
        
    ):
        
        main_model, main_view, main_presenter = self.get_model_view_presenter()
   
    
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
                    shorter_side_pic_2 , shorter_side_3d
                )
            ) + main_presenter.get_similarity_two_nums(
                longer_side_pic_2 , longer_side_3d
            ) / 2
        else:
            result = (
                main_presenter.get_similarity_two_nums(
                    shorter_side_pic_1 , shorter_side_3d
                )
                + main_presenter.get_similarity_two_nums(
                    longer_side_pic_1 , longer_side_3d
                )
            ) / 2
        return result   

    def get_contour_simlarity(self, contour1_2d, contour2_2d, contour_3d):
            closeness_1 = cv2.matchShapes(contour1_2d,contour_3d,1,0.0)
            closeness_2 = cv2.matchShapes(contour2_2d,contour_3d,1,0.0)
            sim = min(closeness_1, closeness_2)
            return sim