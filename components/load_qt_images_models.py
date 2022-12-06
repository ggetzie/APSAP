
from PyQt5 import uic
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtGui import QColor, QIcon, QPixmap, QImage, QWindow, QStandardItem, QStandardItemModel, QMovie, QPainter
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QListWidgetItem, QFileDialog, QMessageBox, QSplashScreen
from ColorSummary import get_brightness_summary_from_2d, get_color_difference, get_color_summary_from_2d
import open3d as o3d
#sample_3d_image
# FILE_ROOT = pathlib.Path("D:\\ararat\\data\\files")
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
        front_photo = QImage(str(photos_dir / "1.jpg"))
        back_photo = QImage(str(photos_dir / "2.jpg"))

        self.findFrontPhoto_l.setPixmap(
            QPixmap.fromImage(front_photo).scaledToWidth(self.findFrontPhoto_l.width())
        )
        self.findBackPhoto_l.setPixmap(
            QPixmap.fromImage(back_photo).scaledToWidth(self.findBackPhoto_l.width())
        )
        self.selected_find.setText(find_num)
        easting_northing_context = self.get_easting_northing_context()
        _3d_locations = self._3d_model_dict[f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find_num)}"]    
       
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
        
        for score_i_j_tuple in sorted(flat_simllarity_list):
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
        _2d_area_image_1 = self.area_comparator.get_2d_picture_area(_2d_image_path_image_1)
        _2d_area_image_2 = self.area_comparator.get_2d_picture_area(_2d_image_path_image_2)    
        #Brightness based simliarity
        color_brightness_2d_image_2 = get_brightness_summary_from_2d(_2d_image_path_image_2)
        color_brightness_2d_image_1 = get_brightness_summary_from_2d(_2d_image_path_image_1)
        
        
        #Let's do the third one: color based similarity
        #Prepare the colors summaries for these two pictures
        front_color = (get_color_summary_from_2d(_2d_image_path_image_1))
        back_color = (get_color_summary_from_2d(_2d_image_path_image_2))  
        #Getting the simlarity scores here 
        similarity_scores = []    
        for i in range(len(self.all_3d_areas)):
            for j in range(len(self.all_3d_areas[i])):
                _3d_area = self.all_3d_areas[i][j][0]
                batch_num = self.all_3d_areas[i][j][1]
                piece_num = self.all_3d_areas[i][j][2]
 
 
  
 
      
           
                color_brightness_3d = (self.all_3d_brightness_summaries[i][j][0][3]) 
                 
                area_similarity = min( max(_3d_area/_2d_area_image_2, _2d_area_image_2/_3d_area) , max(_3d_area/_2d_area_image_1, _2d_area_image_1/_3d_area))
                brightness_similarity = min( max((color_brightness_2d_image_2[3]/1.2)/color_brightness_3d, color_brightness_3d/(color_brightness_2d_image_2[3]/1.2)) , max(color_brightness_3d/(color_brightness_2d_image_1[3]/1.2), (color_brightness_2d_image_1[3]/1.2)/color_brightness_3d))
                #
                brightness_std_similarity = min( max((color_brightness_2d_image_2[-1]/2.2)/color_brightness_3d, color_brightness_3d/(color_brightness_2d_image_2[-1]/2.2)) , max(color_brightness_3d/(color_brightness_2d_image_1[-1]*2.2), (color_brightness_2d_image_1[-1]/2.2)/color_brightness_3d))
                color_similarity = get_color_difference(front_color, back_color  ,(self.all_3d_colors_summaries[i][j]))          
                similarity_scores.append([area_similarity *(2.55/4) + brightness_similarity * (1.4/4) + brightness_std_similarity *(0.045/4)  + color_similarity * (0.005/4), batch_num, piece_num])
                #print(color_brightness_3d)
     

        #print(color_brightness_2d_image_1)
        #print(color_brightness_2d_image_2)
        return similarity_scores