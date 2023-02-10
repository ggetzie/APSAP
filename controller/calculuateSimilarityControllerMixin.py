

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QStandardItem, QStandardItemModel
from PIL.ImageQt import ImageQt
from scipy.stats import gmean, tmean
import numpy as np
import open3d as o3d
from helper.misc import open_image
from config.path_variables import FINDS_SUBDIR, BATCH_3D_SUBDIR, FINDS_PHOTO_DIR, MODELS_FILES_DIR, MODELS_FILES_RE, HEMISPHERES

class CalculateSimilarityControllerMixin:  # bridging the view(gui) and the model(data)
    def __init__(self, view, model):
         
        pass

    def get_similaritiy_scores(self, index,  image_path):
        mainModel, view, controller = self.get_model_view_controller()
        
        _2d_image_path_image_1 = image_path/ "1.jpg"
       
        _2d_image_path_image_2 = image_path/ "2.jpg"

        #Area based similiarity
        _2d_area_image_1 = view.comparator.get_2d_picture_area(_2d_image_path_image_1)
        _2d_area_image_2 = view.comparator.get_2d_picture_area(_2d_image_path_image_2)    
 
        #Brightness based simliarity
        color_brightness_2d_image_2 = view.comparator.get_brightness_summary_from_2d(_2d_image_path_image_2)
        color_brightness_2d_image_1 = view.comparator.get_brightness_summary_from_2d(_2d_image_path_image_1)
        

        #Let's do the third one: color based similarity
        #Prepare the colors summaries for these two pictures
        #Not that useful we found out.
        front_color = (view.comparator.get_color_summary_from_2d(_2d_image_path_image_1))
        back_color = (view.comparator.get_color_summary_from_2d(_2d_image_path_image_2))  
        
        #Fourth one, width length
        _2d_width_length_image_1 = (view.comparator.get_2d_width_length(_2d_image_path_image_1))
        _2d_width_length_image_2 = (view.comparator.get_2d_width_length(_2d_image_path_image_2))
        #Getting the simlarity scores here 
        _2d_area_circle_ratio_image_1 = view.comparator.get_2d_area_circle_ratio(_2d_image_path_image_1)
        _2d_area_circle_ratio_image_2 = view.comparator.get_2d_area_circle_ratio(_2d_image_path_image_2)

        similarity_scores = []    
        
        for i in range(len(view.all_3d_areas)):
           
                _3d_area = view.all_3d_areas[i][0]
                batch_num = view.all_3d_areas[i][1]
                piece_num = view.all_3d_areas[i][2]
                _3d_color = (view.all_3d_colors_summaries[i])
                width_length_3d = view.all_3d_width_length_summaries[i][0]
                    
                color_brightness_3d = (view.all_3d_brightness_summaries[i][0][3]) 
                color_brightness_std_3d = (view.all_3d_brightness_summaries[i][0][-1]) 
                all_3d_area_circle_ratio = view.all_3d_area_circle_ratios[i][0]
           
                similairty = (controller.get_similarity( _3d_area, _2d_area_image_1, _2d_area_image_2, color_brightness_3d, color_brightness_2d_image_1[3], color_brightness_2d_image_2[3], color_brightness_std_3d, color_brightness_2d_image_1[-1], color_brightness_2d_image_2[-1], width_length_3d[0], width_length_3d[1], _2d_width_length_image_1[0], _2d_width_length_image_1[1], _2d_width_length_image_2[0], _2d_width_length_image_2[1], _2d_area_circle_ratio_image_1,_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio ))
                #similarity_scores.append([self.get_3d_2d_simi(color_brightness_3d, color_brightness_std_3d, _3d_area, _2d_area_image_2, _2d_area_image_1, color_brightness_2d_image_2, color_brightness_2d_image_1, front_color, back_color, _3d_color, width_length_3d, _2d_width_length_image_1, _2d_width_length_image_2  ), batch_num, piece_num])
                similarity_scores.append([similairty, batch_num, piece_num])
        return similarity_scores

    def genereate_similiarity_ranked_pieces(self, similarities_list):
        
        grand_similarity = []
        for _threeple in similarities_list:
            vals = _threeple[0]
            grand_similarity.append([[gmean(vals) + tmean(vals)], _threeple[1], _threeple[2]])
        return grand_similarity
    
    def get_area_circle_similarity(self, _2d_area_circle_ratio_image_1,_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio, a, b):
        mainModel, view, controller = self.get_model_view_controller()
        if(controller.get_similarity_two_nums(_2d_area_circle_ratio_image_1, all_3d_area_circle_ratio) >  controller.get_similarity_two_nums(_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio) ):
            
             return controller.get_similarity_two_nums(_2d_area_circle_ratio_image_2 * a + b, all_3d_area_circle_ratio)  
        else:
             return controller.get_similarity_two_nums(_2d_area_circle_ratio_image_1 * a + b, all_3d_area_circle_ratio)  

    def get_similarity(self, _3d_area, _2d_area_1, _2d_area_2, _3d_brightness, _2d_brightness_1, _2d_brightness_2, _3d_brightness_std, _2d_brightness_std_1, _2d_brightness_std_2, _3d_pic_side_1, _3d_pic_side_2, _first_pic_side_1, _first_pic_side_2, _second_pic_side_1, _second_pic_side_2,  _2d_area_circle_ratio_image_1,_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio):
        mainModel, view, controller = self.get_model_view_controller()
         
        parameters = mainModel.parameters
        area_similarity = controller.get_area_similarity(_3d_area, _2d_area_1, _2d_area_2,parameters["area"]["slope"], parameters["area"]["intercept"])
        brightness_similarity = controller.get_brightness_similarity(_3d_brightness, _2d_brightness_1, _2d_brightness_2,parameters["brightness"]["slope"], parameters["brightness"]["intercept"])
        brightness_std_similarity = controller.get_brightness_std_similarity(_3d_brightness_std, _2d_brightness_std_1, _2d_brightness_std_2,parameters["brightness_std"]["slope"], parameters["brightness_std"]["intercept"])
        width_length_similarity = controller.get_width_length_similarity(_3d_pic_side_1, _3d_pic_side_2, _first_pic_side_1,  _first_pic_side_2, _second_pic_side_1, _second_pic_side_2,parameters["width"]["slope"], parameters["width"]["intercept"],parameters["length"]["slope"], parameters["length"]["intercept"])
        area_circle_similarity = controller.get_area_circle_similarity(_2d_area_circle_ratio_image_1,_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio, 0.9055558282782922, 0.03996414943733839)
        total_similarity = area_similarity + brightness_similarity + brightness_std_similarity + width_length_similarity
        #weights = np.array([0.4, 0.38, 0.12, 0.1])
        #weights = np.array([2.85877858e-01 ,7.14122142e-01 ,0.00000000e+00, 5.55111512e-17, 0.1])
        similarities = np.array([area_similarity, brightness_similarity, brightness_std_similarity, width_length_similarity, area_circle_similarity])
        #return np.dot(weights, similarities)# total_similarity/4
        return similarities
        #return area_circle_similarity

    


    def get_similarity_two_nums(self, a, b): #a, b >

        #A new similiarity function
        return abs(a - b) / (a + b) #If they are the same, it becomes zeros, if their difference approaches infinitry, it becomes 1.
 

    def get_area_similarity(self, _3d_area, _2d_area_1, _2d_area_2, a, b):
        mainModel, view, controller = self.get_model_view_controller()

        #Assumtion 1: there is a linear relation between the _3d_area and the _2d_area
        #The parameters a, b are found by running a linear regression between all_3d_areas and all the _2d_area(picked from the closer of the two)
        #We compare the 3d model's area with two pictures. Possible future improvement is to compare two 2d areas with two 3d areas.
        smaller_area = min(_2d_area_1, _2d_area_2)
        larger_area = max(_2d_area_1, _2d_area_2)

        #We only calculuate the similirity based upon the more simliar image in terms of the area regardless a and b.
        if(controller.get_similarity_two_nums(smaller_area, _3d_area) >  controller.get_similarity_two_nums(larger_area, _3d_area) ):
            #We use a and b to get a more accurate similarity.
            return controller.get_similarity_two_nums(larger_area * a + b, _3d_area)  
        else:
             return controller.get_similarity_two_nums(smaller_area * a + b, _3d_area)  
 

    def get_brightness_similarity(self, _3d_brightness, _2d_brightness_1, _2d_brightness_2, a, b):
        #Similiar reasoning behind function get_area_similarity()
        mainModel, view, controller = self.get_model_view_controller()
         
        darker_brightness = min(_2d_brightness_1, _2d_brightness_2)
        brighter_brightness = max(_2d_brightness_1, _2d_brightness_2)

        if(controller.get_similarity_two_nums(darker_brightness, _3d_brightness) >  controller.get_similarity_two_nums(brighter_brightness, _3d_brightness) ):
           
            return controller.get_similarity_two_nums(brighter_brightness * a + b, _3d_brightness)  
        else:
             return controller.get_similarity_two_nums(darker_brightness * a + b, _3d_brightness)  
    
    def get_brightness_std_similarity(self, _3d_brightness_std, _2d_brightness_std_1, _2d_brightness_std_2, a, b):
        #Similiar reasoning behind function get_area_similarity()
        mainModel, view, controller = self.get_model_view_controller()
         
        smaller_brightness_std = min(_2d_brightness_std_1, _2d_brightness_std_2)
        larger_brightness_std = max(_2d_brightness_std_1, _2d_brightness_std_2)

         
        if(controller.get_similarity_two_nums(smaller_brightness_std, _3d_brightness_std) >  controller.get_similarity_two_nums(larger_brightness_std, _3d_brightness_std) ):
           
            return controller.get_similarity_two_nums(larger_brightness_std * a + b, _3d_brightness_std)  
        else:
             return controller.get_similarity_two_nums(smaller_brightness_std * a + b, _3d_brightness_std)  
    

    def get_width_length_similarity(self, _3d_pic_side_1, _3d_pic_side_2, _first_pic_side_1, _first_pic_side_2, _second_pic_side_1, _second_pic_side_2, a, b, c, d):
        #Similiar reasoning behind function get_area_similarity()
        mainModel, view, controller = self.get_model_view_controller()

        longer_side_3d = max(_3d_pic_side_1, _3d_pic_side_2)
        shorter_side_3d = min(_3d_pic_side_1, _3d_pic_side_2)
        
       
        longer_side_pic_1 = max(_first_pic_side_1,_first_pic_side_2 )
        shorter_side_pic_1 = min(_first_pic_side_1,_first_pic_side_2 )
 
        longer_side_pic_2 = max(_second_pic_side_1,_second_pic_side_2 )
        shorter_side_pic_2 = min(_second_pic_side_1,_second_pic_side_2 )

        #if without linear adjustment, the image is closer, the image is the one we pick. //For now, arithematic mean is used, other types of mean maybe considered later
        unadjusted_similarity_1  = (controller.get_similarity_two_nums(longer_side_pic_1, longer_side_3d ) +  controller.get_similarity_two_nums( shorter_side_pic_1, shorter_side_3d ))/2
        unadjusted_similarity_2  = (controller.get_similarity_two_nums(longer_side_pic_2, longer_side_3d ) +  controller.get_similarity_two_nums(shorter_side_pic_2, shorter_side_3d))/2
        if(unadjusted_similarity_1 > unadjusted_similarity_2):
            result = (controller.get_similarity_two_nums( shorter_side_pic_2* a + b, shorter_side_3d ))+ controller.get_similarity_two_nums(longer_side_pic_2* c + d, longer_side_3d   ) /2
        else:
            result = (controller.get_similarity_two_nums( shorter_side_pic_1* a + b, shorter_side_3d ) + controller.get_similarity_two_nums(longer_side_pic_1* c + d, longer_side_3d   ) )/2
       
        return  result
