
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


class LoadImagesModels:

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
        flat_simllarity_list  = self.get_similaritiy_scores(find_num, _2d_image_path)
      
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
 


    
    def get_similaritiy_scores(self, index,  image_path):
        _2d_image_path_image_1 = image_path/ "1.jpg"
       
        _2d_image_path_image_2 = image_path/ "2.jpg"

        #Area based similiarity
        _2d_area_image_1 = self.comparator.get_2d_picture_area(_2d_image_path_image_1)
        _2d_area_image_2 = self.comparator.get_2d_picture_area(_2d_image_path_image_2)    

        print(_2d_area_image_1)
        print(_2d_area_image_2)
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
        similarity_scores = []    


        for i in range(len(self.all_3d_areas)):
           
                _3d_area = self.all_3d_areas[i][0]
                batch_num = self.all_3d_areas[i][1]
                piece_num = self.all_3d_areas[i][2]
                _3d_color = (self.all_3d_colors_summaries[i])
                width_length_3d = self.all_3d_width_length_summaries[i][0]
                    
                color_brightness_3d = (self.all_3d_brightness_summaries[i][0][3]) 
                color_brightness_std_3d = (self.all_3d_brightness_summaries[i][0][-1]) 
 
           
                
                similarity_scores.append([self.get_3d_2d_simi(color_brightness_3d, color_brightness_std_3d, _3d_area, _2d_area_image_2, _2d_area_image_1, color_brightness_2d_image_2, color_brightness_2d_image_1, front_color, back_color, _3d_color, width_length_3d, _2d_width_length_image_1, _2d_width_length_image_2  ), batch_num, piece_num])
                
        return similarity_scores


    def get_3d_2d_simi(self, color_brightness_3d, color_brightness_std_3d, _3d_area, _2d_area_image_2, _2d_area_image_1, color_brightness_2d_image_2, color_brightness_2d_image_1, front_color, back_color, _3d_color, width_length_3d, _2d_width_length_image_1, _2d_width_length_image_2  ):
        area_similarity = min( max(_3d_area/_2d_area_image_2, _2d_area_image_2/_3d_area) , max(_3d_area/_2d_area_image_1, _2d_area_image_1/_3d_area))
        brightness_similarity = min( max((color_brightness_2d_image_2[3]/1.2)/color_brightness_3d, color_brightness_3d/(color_brightness_2d_image_2[3]/1.2)) , max(color_brightness_3d/(color_brightness_2d_image_1[3]/1.2), (color_brightness_2d_image_1[3]/1.2)/color_brightness_3d))
        brightness_std_similarity = min( max((color_brightness_2d_image_2[-1]/2.1)/color_brightness_std_3d, color_brightness_std_3d/(color_brightness_2d_image_2[-1]/2.1)) , max(color_brightness_std_3d/(color_brightness_2d_image_1[-1]/2.1), (color_brightness_2d_image_1[-1]/2.1)/color_brightness_std_3d))
        color_similarity = self.comparator.get_color_difference(front_color, back_color  ,_3d_color)          
        width_length_simlarity_with_image_1  = (max (width_length_3d[0]/_2d_width_length_image_1[0],_2d_width_length_image_1[0]/  width_length_3d[0]) +  max (width_length_3d[1]/_2d_width_length_image_1[1],_2d_width_length_image_1[1]/  width_length_3d[1]))/2
        width_length_simlarity_with_image_2  = (max (width_length_3d[0]/_2d_width_length_image_2[0],_2d_width_length_image_2[0]/  width_length_3d[0]) +  max (width_length_3d[1]/_2d_width_length_image_2[1],_2d_width_length_image_2[1]/  width_length_3d[1]))/2
        width_length_simlarity = min (width_length_simlarity_with_image_1, width_length_simlarity_with_image_2)
        all_similarities = np.array([area_similarity, brightness_similarity, width_length_simlarity,  brightness_std_similarity, color_similarity])
        multipliers = np.array([90, 65, 40,5, 0.15])
        result = np.dot(all_similarities, multipliers) /np.sum(multipliers) #Now we reduce it to a number close to 1, the closer it is to one, the more accurate the prediction it is.
        
        
        return result

    def ratio_larger_than_1(self, a, b):
        #When we compare two numbers and assess if they are close, we reorder the divider and dividend to make sure the ratio is larger than 1, so that we can use the ratio as a similarity matric
        #E.g. We can't easily compare 0.2 and 1.8 and say which ratio indicates a better similarity score, but we can compare 1.2 and 1.8 and say 1.2 is a better similiar score.
        if (a > b):
            return a/b
        else:
            return b/a
         

    def get_area_similarity(self, _3d_area, _2d_area_1, _2d_area_2, a, b):
        #Assumtion 1: there is a linear relation between the _3d_area and the _2d_area
        #We compare the 3d model's area with two pictures. Possible future improvement is to compare two 2d areas with two 3d areas.
        smaller_area_ = min(_2d_area_1, _2d_area_2)
        larger_area = max(_2d_area_1, _2d_area_2)

        #We assume there is a linear relationship between the the 3d area and the 2d area
        small_ratio = self.ratio_larger_than_1(smaller_area_ * a + b, _3d_area)
        large__ratio = self.ratio_larger_than_1(larger_area * a + b, _3d_area)

        #We assume the better result indicates the actual similairty
        return min(large__ratio, small_ratio)

    def get_brightness_similarity(self, _3d_brightness, _2d_brightness_1, _2d_brightness_2, a, b):
        #Similiar reasoning behind function get_area_similarity()
         
        darker_brightness = min(_2d_brightness_1, _2d_brightness_2)
        brighter_brightness = max(_2d_brightness_1, _2d_brightness_2)

         
        darker_ratio = ratio_larger_than_1(darker_brightness * a + b, _3d_brightness)
        brighter__ratio = ratio_larger_than_1(brighter_brightness * a + b, _3d_brightness)

        return min(darker_ratio, brighter__ratio)


    def get_brightness_similairty(self, color_brightness_3d, color_brightness_2d_1, color_brightness_2d_2, abc):
        pass
    def get_similarity(self):
        #A new function to get the similarity.
        #Consider area similarity:
        #   The old function is find the
        pass

 