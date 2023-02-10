from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QStandardItem, QStandardItemModel
from PIL.ImageQt import ImageQt
import open3d as o3d
from helper.misc import open_image
from config.path_variables import FINDS_SUBDIR, FINDS_PHOTO_DIR, MODELS_FILES_DIR

class Load1jpgPairController:  # bridging the view(gui) and the model(data)
    def __init__(self, view, model):
        # Notice this object is the controller, that which connects the view(GUI) and the model(data)
        pass


    def load_find_images(self, selected_item):
     
        mainModel, view, controller = self.get_model_view_controller()


        view.selected_find_widget = selected_item
        try:
            find_num = view.findsList.currentItem().text()
        except AttributeError:
            view.findFrontPhoto_l.clear()
            view.findBackPhoto_l.clear()
            return
        

        photos_dir = view.mainController.get_context_dir() / FINDS_SUBDIR / find_num / FINDS_PHOTO_DIR
        view.path_2d_picture = photos_dir
        import time
        now = time.time()
        front_photo = ImageQt(open_image(str(photos_dir / "1.jpg"), full_size=False))
         
        back_photo =  ImageQt(open_image(str(photos_dir / "2.jpg"), full_size=False))
        #
        print(f"time passed: {time.time() - now}")
        view.findFrontPhoto_l.setPixmap(
            QPixmap.fromImage(front_photo).scaledToWidth(view.findFrontPhoto_l.width())
        )
        view.findBackPhoto_l.setPixmap(
            QPixmap.fromImage(back_photo).scaledToWidth(view.findBackPhoto_l.width())
        )
        view.selected_find.setText(find_num)
        easting_northing_context = view.mainController.get_easting_northing_context()
        _3d_locations = view._3d_model_dict[f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find_num)}"]    

        #If we already matched the 
        if _3d_locations[0] != None and _3d_locations[1] != None:
            view.current_batch.setText(str(_3d_locations[0]))
            view.current_piece.setText(str(_3d_locations[1]))
            #Change to the piece matched as default
          
            path =  (str((controller.get_context_dir()/MODELS_FILES_DIR)))
            whole_path = (path.replace("*", f"{int(_3d_locations[0]):03}", 1).replace("*", f"{int(_3d_locations[1])}", 1)) 
            current_pcd_load = o3d.io.read_point_cloud(whole_path)
            if hasattr(view, "current_pcd") :
                controller.change_model(current_pcd_load, view.current_pcd)
            else:
                controller.change_model(current_pcd_load, None)
                
        else:
            view.current_batch.setText("NS")
            view.current_piece.setText("NS")
            if hasattr(view, "current_pcd"):
                view.plyWindow.remove_geometry(view.current_pcd)
                view.current_pcd = None
            #Here let's remove the 3d model
            
            
        #We have an image chosen, we can get the simlarity scores against all 3d model's images
        _2d_image_path = photos_dir 

        #Previously, here is simply a list of (val, batch  piece))
        #Now the value become area_similarity, brightness_similarity, brightness_std_similarity, width_length_similarity, area_circle_similarity, batch, piece)


        old_flat_similairy_list = []



        flat_simllarity_list  = controller.get_similaritiy_scores(find_num, _2d_image_path)

        #[area_similarity, brightness_similarity, brightness_std_similarity, width_length_similarity, area_circle_similarity]

 
 
      
        #flat_simllarity_list = old_flat_similairy_list
        flat_simllarity_list =     controller.genereate_similiarity_ranked_pieces(flat_simllarity_list)
     
        all_matched_3d_models = set()
        
        for key in (view._3d_model_dict):
            if not (view._3d_model_dict[key][0] == None and view._3d_model_dict[key][1] == None):
                all_matched_3d_models.add(view._3d_model_dict[key])
     
    
        #python sort by first element of list by default

        model = QStandardItemModel(view)
        model.setHorizontalHeaderLabels(["Sorted models"])
  
         
        
        for i, score_i_j_tuple in enumerate(sorted(flat_simllarity_list)):
      
            
            ply = QStandardItem(f"Batch {score_i_j_tuple[1]}, model: {score_i_j_tuple[2]}")
            path =  (str((controller.get_context_dir()/MODELS_FILES_DIR)))
            whole_path = (path.replace("*", f"{int(score_i_j_tuple[1]):03}", 1).replace("*", f"{int(score_i_j_tuple[2])}", 1)) 
            if (int(score_i_j_tuple[1]), int(score_i_j_tuple[2])) in all_matched_3d_models:
                    ply.setForeground(QColor("red"))
            ply.setData(f"{whole_path}", Qt.UserRole) 
            
            model.appendRow(ply)
 
        view.sortedModelList.setModel(model)
        view.sortedModelList.selectionModel().currentChanged.connect(controller.change_3d_model)
 
