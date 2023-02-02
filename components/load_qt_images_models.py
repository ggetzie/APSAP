
from PyQt5 import uic
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtGui import QColor, QIcon, QPixmap, QImage, QWindow, QStandardItem, QStandardItemModel, QMovie, QPainter
from PIL.ImageQt import ImageQt

import numpy as np
import open3d as o3d
from misc import open_image
from database_tools import get_pottery_sherd_info
FINDS_SUBDIR = "finds/individual"
BATCH_3D_SUBDIR = "finds/3dbatch"
FINDS_PHOTO_DIR = "photos"
MODELS_FILES_DIR = "finds/3dbatch/2022/batch_*/registration_reso1_maskthres242/final_output/piece_*_world.ply"
MODELS_FILES_RE = "finds/3dbatch/2022/batch_(.+?)/registration_reso1_maskthres242/final_output/piece_(.+?)_world.ply"
HEMISPHERES = ("N", "S")
import math
from scipy.stats import gmean, tmean
class LoadImagesModels:



    def genereate_similiarity_ranked_pieces(similarities_list):
        #Now the value become area_similarity, brightness_similarity, brightness_std_similarity, width_length_similarity, area_circle_similarity, batch, piece)
        pass

    def load_find_images(self, selected_item):
        self.selected_find_widget = selected_item
        try:
            find_num = self.findsList.currentItem().text()
        except AttributeError:
            self.findFrontPhoto_l.clear()
            self.findBackPhoto_l.clear()
            return
        

        photos_dir = self.get_context_dir() / FINDS_SUBDIR / find_num / FINDS_PHOTO_DIR
        self.path_2d_picture = photos_dir
        import time
        now = time.time()
        front_photo = ImageQt(open_image(str(photos_dir / "1.jpg"), full_size=False))
         
        back_photo =  ImageQt(open_image(str(photos_dir / "2.jpg"), full_size=False))
        #
        print(f"time passed: {time.time() - now}")
        self.findFrontPhoto_l.setPixmap(
            QPixmap.fromImage(front_photo).scaledToWidth(self.findFrontPhoto_l.width())
        )
        self.findBackPhoto_l.setPixmap(
            QPixmap.fromImage(back_photo).scaledToWidth(self.findBackPhoto_l.width())
        )
        self.selected_find.setText(find_num)
        easting_northing_context = self.get_easting_northing_context()
        _3d_locations = self._3d_model_dict[f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find_num)}"]    

        #If we already matched the 
        if _3d_locations[0] != None and _3d_locations[1] != None:
            self.current_batch.setText(str(_3d_locations[0]))
            self.current_piece.setText(str(_3d_locations[1]))
            #Change to the piece matched as default
          
            path =  (str((self.get_context_dir()/MODELS_FILES_DIR)))
            whole_path = (path.replace("*", f"{int(_3d_locations[0]):03}", 1).replace("*", f"{int(_3d_locations[1])}", 1)) 
            current_pcd_load = o3d.io.read_point_cloud(whole_path)
            if hasattr(self, "current_pcd") :
                self.change_model(current_pcd_load, self.current_pcd)
            else:
                self.change_model(current_pcd_load, None)
                
        else:
            self.current_batch.setText("NS")
            self.current_piece.setText("NS")
            if hasattr(self, "current_pcd"):
                self.vis.remove_geometry(self.current_pcd)
                self.current_pcd = None
            #Here let's remove the 3d model
            
            
        #We have an image chosen, we can get the simlarity scores against all 3d model's images
        _2d_image_path = photos_dir 

        #Previously, here is simply a list of (val, batch  piece))
        #Now the value become area_similarity, brightness_similarity, brightness_std_similarity, width_length_similarity, area_circle_similarity, batch, piece)


        old_flat_similairy_list = []



        flat_simllarity_list  = self.get_similaritiy_scores(find_num, _2d_image_path)

        #[area_similarity, brightness_similarity, brightness_std_similarity, width_length_similarity, area_circle_similarity]








        for i in (flat_simllarity_list):
            temp = []
            scores = i[0]
            temp.append(gmean(scores ) + tmean(scores))
            temp.append(i[1])
            temp.append(i[2])
            old_flat_similairy_list.append(temp)

        flat_simllarity_list = old_flat_similairy_list
        all_matched_3d_models = set()
        
        for key in (self._3d_model_dict):
            if not (self._3d_model_dict[key][0] == None and self._3d_model_dict[key][1] == None):
                all_matched_3d_models.add(self._3d_model_dict[key])
     
    
        #python sort by first element of list by default
     
        model = QStandardItemModel(self)
        model.setHorizontalHeaderLabels(["Sorted models"])
  
         
        
        for i, score_i_j_tuple in enumerate(sorted(flat_simllarity_list)):
      
            
            ply = QStandardItem(f"Batch {score_i_j_tuple[1]}, model: {score_i_j_tuple[2]}")
            path =  (str((self.get_context_dir()/MODELS_FILES_DIR)))
            whole_path = (path.replace("*", f"{int(score_i_j_tuple[1]):03}", 1).replace("*", f"{int(score_i_j_tuple[2])}", 1)) 
            if (int(score_i_j_tuple[1]), int(score_i_j_tuple[2])) in all_matched_3d_models:
                    ply.setForeground(QColor("red"))
            ply.setData(f"{whole_path}", Qt.UserRole) 
            
            model.appendRow(ply)
 
        self.sortedModelList.setModel(model)
        self.sortedModelList.selectionModel().currentChanged.connect(self.change_3d_model)
 

    def get_area_circle_similarity(self, _2d_area_circle_ratio_image_1,_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio, a, b):

        if(self.get_similarity_two_nums(_2d_area_circle_ratio_image_1, all_3d_area_circle_ratio) >  self.get_similarity_two_nums(_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio) ):
            
             return self.get_similarity_two_nums(_2d_area_circle_ratio_image_2 * a + b, all_3d_area_circle_ratio)  
        else:
             return self.get_similarity_two_nums(_2d_area_circle_ratio_image_1 * a + b, all_3d_area_circle_ratio)  

    def get_similarity(self, _3d_area, _2d_area_1, _2d_area_2, _3d_brightness, _2d_brightness_1, _2d_brightness_2, _3d_brightness_std, _2d_brightness_std_1, _2d_brightness_std_2, _3d_pic_side_1, _3d_pic_side_2, _first_pic_side_1, _first_pic_side_2, _second_pic_side_1, _second_pic_side_2,  _2d_area_circle_ratio_image_1,_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio):

        parameters = self.parameters
        area_similarity = self.get_area_similarity(_3d_area, _2d_area_1, _2d_area_2,parameters["area"]["slope"], parameters["area"]["intercept"])
        brightness_similarity = self.get_brightness_similarity(_3d_brightness, _2d_brightness_1, _2d_brightness_2,parameters["brightness"]["slope"], parameters["brightness"]["intercept"])
        brightness_std_similarity = self.get_brightness_std_similarity(_3d_brightness_std, _2d_brightness_std_1, _2d_brightness_std_2,parameters["brightness_std"]["slope"], parameters["brightness_std"]["intercept"])
        width_length_similarity = self.get_width_length_similarity(_3d_pic_side_1, _3d_pic_side_2, _first_pic_side_1,  _first_pic_side_2, _second_pic_side_1, _second_pic_side_2,parameters["width"]["slope"], parameters["width"]["intercept"],parameters["length"]["slope"], parameters["length"]["intercept"])
        area_circle_similarity = self.get_area_circle_similarity(_2d_area_circle_ratio_image_1,_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio, 0.9055558282782922, 0.03996414943733839)
        total_similarity = area_similarity + brightness_similarity + brightness_std_similarity + width_length_similarity
        #weights = np.array([0.4, 0.38, 0.12, 0.1])
        #weights = np.array([2.85877858e-01 ,7.14122142e-01 ,0.00000000e+00, 5.55111512e-17, 0.1])
        similarities = np.array([area_similarity, brightness_similarity, brightness_std_similarity, width_length_similarity, area_circle_similarity])
        #return np.dot(weights, similarities)# total_similarity/4
        return similarities
        #return area_circle_similarity

    
    def get_similaritiy_scores(self, index,  image_path):
        _2d_image_path_image_1 = image_path/ "1.jpg"
       
        _2d_image_path_image_2 = image_path/ "2.jpg"

        #Area based similiarity
        _2d_area_image_1 = self.comparator.get_2d_picture_area(_2d_image_path_image_1)
        _2d_area_image_2 = self.comparator.get_2d_picture_area(_2d_image_path_image_2)    
 
        #Brightness based simliarity
        color_brightness_2d_image_2 = self.comparator.get_brightness_summary_from_2d(_2d_image_path_image_2)
        color_brightness_2d_image_1 = self.comparator.get_brightness_summary_from_2d(_2d_image_path_image_1)
        

        #Let's do the third one: color based similarity
        #Prepare the colors summaries for these two pictures
        #Not that useful we found out.
        front_color = (self.comparator.get_color_summary_from_2d(_2d_image_path_image_1))
        back_color = (self.comparator.get_color_summary_from_2d(_2d_image_path_image_2))  
        
        #Fourth one, width length
        _2d_width_length_image_1 = (self.comparator.get_2d_width_length(_2d_image_path_image_1))
        _2d_width_length_image_2 = (self.comparator.get_2d_width_length(_2d_image_path_image_2))
        #Getting the simlarity scores here 
        _2d_area_circle_ratio_image_1 = self.comparator.get_2d_area_circle_ratio(_2d_image_path_image_1)
        _2d_area_circle_ratio_image_2 = self.comparator.get_2d_area_circle_ratio(_2d_image_path_image_2)

        similarity_scores = []    
        
        for i in range(len(self.all_3d_areas)):
           
                _3d_area = self.all_3d_areas[i][0]
                batch_num = self.all_3d_areas[i][1]
                piece_num = self.all_3d_areas[i][2]
                _3d_color = (self.all_3d_colors_summaries[i])
                width_length_3d = self.all_3d_width_length_summaries[i][0]
                    
                color_brightness_3d = (self.all_3d_brightness_summaries[i][0][3]) 
                color_brightness_std_3d = (self.all_3d_brightness_summaries[i][0][-1]) 
                all_3d_area_circle_ratio = self.all_3d_area_circle_ratios[i][0]
           
                similairty = (self.get_similarity( _3d_area, _2d_area_image_1, _2d_area_image_2, color_brightness_3d, color_brightness_2d_image_1[3], color_brightness_2d_image_2[3], color_brightness_std_3d, color_brightness_2d_image_1[-1], color_brightness_2d_image_2[-1], width_length_3d[0], width_length_3d[1], _2d_width_length_image_1[0], _2d_width_length_image_1[1], _2d_width_length_image_2[0], _2d_width_length_image_2[1], _2d_area_circle_ratio_image_1,_2d_area_circle_ratio_image_2, all_3d_area_circle_ratio ))
                #similarity_scores.append([self.get_3d_2d_simi(color_brightness_3d, color_brightness_std_3d, _3d_area, _2d_area_image_2, _2d_area_image_1, color_brightness_2d_image_2, color_brightness_2d_image_1, front_color, back_color, _3d_color, width_length_3d, _2d_width_length_image_1, _2d_width_length_image_2  ), batch_num, piece_num])
                similarity_scores.append([similairty, batch_num, piece_num])
        return similarity_scores

 

    def get_similarity_two_nums(self, a, b): #a, b >

        #A new similiarity function
        return abs(a - b) / (a + b) #If they are the same, it becomes zeros, if their difference approaches infinitry, it becomes 1.
                
        """
        Depreciated
        When we compare two numbers and assess if they are close, we reorder the divider and dividend to make sure the ratio is larger than 1, so that we can use the ratio as a similarity matric
        E.g. We can't easily compare 0.2 and 1.8 and say which ratio indicates a better similarity score, but we can compare 1.2 and 1.8 and say 1.2 is a better similiar score.
        if (a > b):
            return a/b
        else:
            return b/a
        
        """

    def get_area_similarity(self, _3d_area, _2d_area_1, _2d_area_2, a, b):
        #Assumtion 1: there is a linear relation between the _3d_area and the _2d_area
        #The parameters a, b are found by running a linear regression between all_3d_areas and all the _2d_area(picked from the closer of the two)
        #We compare the 3d model's area with two pictures. Possible future improvement is to compare two 2d areas with two 3d areas.
        smaller_area = min(_2d_area_1, _2d_area_2)
        larger_area = max(_2d_area_1, _2d_area_2)

        #We only calculuate the similirity based upon the more simliar image in terms of the area regardless a and b.
        if(self.get_similarity_two_nums(smaller_area, _3d_area) >  self.get_similarity_two_nums(larger_area, _3d_area) ):
            #We use a and b to get a more accurate similarity.
            return self.get_similarity_two_nums(larger_area * a + b, _3d_area)  
        else:
             return self.get_similarity_two_nums(smaller_area * a + b, _3d_area)  
 

    def get_brightness_similarity(self, _3d_brightness, _2d_brightness_1, _2d_brightness_2, a, b):
        #Similiar reasoning behind function get_area_similarity()
         
        darker_brightness = min(_2d_brightness_1, _2d_brightness_2)
        brighter_brightness = max(_2d_brightness_1, _2d_brightness_2)

        if(self.get_similarity_two_nums(darker_brightness, _3d_brightness) >  self.get_similarity_two_nums(brighter_brightness, _3d_brightness) ):
           
            return self.get_similarity_two_nums(brighter_brightness * a + b, _3d_brightness)  
        else:
             return self.get_similarity_two_nums(darker_brightness * a + b, _3d_brightness)  
    
    def get_brightness_std_similarity(self, _3d_brightness_std, _2d_brightness_std_1, _2d_brightness_std_2, a, b):
        #Similiar reasoning behind function get_area_similarity()
         
        smaller_brightness_std = min(_2d_brightness_std_1, _2d_brightness_std_2)
        larger_brightness_std = max(_2d_brightness_std_1, _2d_brightness_std_2)

         
        if(self.get_similarity_two_nums(smaller_brightness_std, _3d_brightness_std) >  self.get_similarity_two_nums(larger_brightness_std, _3d_brightness_std) ):
           
            return self.get_similarity_two_nums(larger_brightness_std * a + b, _3d_brightness_std)  
        else:
             return self.get_similarity_two_nums(smaller_brightness_std * a + b, _3d_brightness_std)  
    

    def get_width_length_similarity(self, _3d_pic_side_1, _3d_pic_side_2, _first_pic_side_1, _first_pic_side_2, _second_pic_side_1, _second_pic_side_2, a, b, c, d):
        #Similiar reasoning behind function get_area_similarity()

        longer_side_3d = max(_3d_pic_side_1, _3d_pic_side_2)
        shorter_side_3d = min(_3d_pic_side_1, _3d_pic_side_2)
        
       
        longer_side_pic_1 = max(_first_pic_side_1,_first_pic_side_2 )
        shorter_side_pic_1 = min(_first_pic_side_1,_first_pic_side_2 )
 
        longer_side_pic_2 = max(_second_pic_side_1,_second_pic_side_2 )
        shorter_side_pic_2 = min(_second_pic_side_1,_second_pic_side_2 )

        #if without linear adjustment, the image is closer, the image is the one we pick. //For now, arithematic mean is used, other types of mean maybe considered later
        unadjusted_similarity_1  = (self.get_similarity_two_nums(longer_side_pic_1, longer_side_3d ) +  self.get_similarity_two_nums( shorter_side_pic_1, shorter_side_3d ))/2
        unadjusted_similarity_2  = (self.get_similarity_two_nums(longer_side_pic_2, longer_side_3d ) +  self.get_similarity_two_nums(shorter_side_pic_2, shorter_side_3d))/2
        if(unadjusted_similarity_1 > unadjusted_similarity_2):
            result = (self.get_similarity_two_nums( shorter_side_pic_2* a + b, shorter_side_3d ))+ self.get_similarity_two_nums(longer_side_pic_2* c + d, longer_side_3d   ) /2
        else:
            result = (self.get_similarity_two_nums( shorter_side_pic_1* a + b, shorter_side_3d ) + self.get_similarity_two_nums(longer_side_pic_1* c + d, longer_side_3d   ) )/2
       
        return  result


 