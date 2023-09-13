 
from PyQt5.QtCore import Qt


from PyQt5.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)
from glob import glob as glob
from pathlib import Path
import re
 


class LoadPlys:

    def populate_models(self):

      
        main_model, main_view, main_presenter = self.get_model_view_presenter()    
        
        #Qt associates a model with a select object. 
        self.reset_ply_selection_model()

        #Measurements are used for similaritiy calculuation
        # self.reset_ply_measurements()
    
        #models of the current folder are grouped by batches they belong to
        batched_models = self.get_batched_models()


        years_models = (self.get_year_models())
        #We must know the 3d models that were matched with a pair of jpgs, 
        matched_plys = self.get_matched_plys(main_view._3d_model_dict)

        
        for year in sorted(years_models.keys()):
            year_item = QStandardItem(f"{year}")
            for batch in sorted(years_models[year].keys()):
                batch_item =  QStandardItem(f"{batch}")
                for piece in sorted(years_models[year][batch].keys()):
                   modelPiece = QStandardItem(f"{piece}")
        # Go through each batch

        for batch in batched_models:
            

            model_batch = QStandardItem(f"{batch}")
            pieces = batched_models[batch]
            batch_num = int(batch)
            #Go through each piece of the current batch
            for piece in pieces:
                piece_num = piece[0]
                path = piece[1]
                year = piece[2]
                
 
                #Create a piece q item later for use
                modelPiece = QStandardItem(f"{piece_num}")
                modelPiece.setData(f"{path}", Qt.UserRole)
               
                #Set the color of the item to be red if it already had a match before
                if (int(batch_num), int(piece_num)) in matched_plys:
                    modelPiece.setForeground(QColor("red"))
               
               
                model_batch.appendRow(modelPiece)
           
           
            main_view.modelList.selectionModel().model().appendRow(model_batch)

    def reset_ply_selection_model(self):
        #Either create a model for the selection model instance, or remove all the rows in it
        main_model, main_view, main_presenter = self.get_model_view_presenter()    

        if not main_view.modelList.selectionModel():
            model = QStandardItemModel(main_view)
            model.setHorizontalHeaderLabels(["Models"])
            main_view.modelList.setModel(model)
            main_view.modelList.selectionModel().currentChanged.connect(main_presenter.change_3d_model)
        else:
            main_view.modelList.selectionModel().model().removeRows(0, main_view.modelList.selectionModel().model().rowCount())

    def get_contour_3d (self,  model_path):
        import numpy as np
        import open3d as o3d
        from PIL import Image
        import cv2
        main_model, main_view, main_presenter = self.get_model_view_presenter()    

        ply_window = main_view.ply_window
        ply_window.clear_geometries()
        current_pcd_load = o3d.io.read_point_cloud(model_path) 
        
        ply_window.add_geometry(current_pcd_load)
        ctr = ply_window.get_view_control()
            
        ply_window.get_render_option().point_size = 5

        ctr.change_field_of_view(step=-9)
        object_image = ply_window.capture_screen_float_buffer(True)
        
        pic = np.array(Image.fromarray( np.multiply(np.array(object_image), 255).astype(np.uint8)).convert('L'))#(np.array(Image.fromarray( np.multiply(np.array(object_image), 255).astype(np.uint8)).convert('L')).ravel())
        pic[pic==255] = 0
        pic[pic != 0] = 255
        
        pil_image = Image.fromarray(pic).convert("RGB")
      
        open_cv_image = np.array(pil_image) 
    # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        img_gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        ret, thresh = cv2.threshold(img_gray, 127, 255,0)
        contours, hierarchy  = cv2.findContours(thresh,2,1)
        cnt1 = contours[0]
        ply_window.remove_geometry(current_pcd_load)
        del ctr
        return cnt1
 
    def load_ply_info_from_cache_or_calc(self, path):
        
        main_model, main_view, main_presenter = self.get_model_view_presenter() 
        import diskcache
         
  
        cache_result = main_model.cache_3d.get(path)
        m = re.search(
                main_model.path_variables["MODELS_FILES_RE"],
            path.replace("\\", "/"),
        )
        year = (m.group(1))
        batch_num = m.group(2)
        piece_num = m.group(3)
        if cache_result and (type(cache_result) is tuple ) and len(cache_result) == 7 :
            print(f"Point cloud's data has been stored. Loading {path} directly from library")
            cache_result = list(cache_result)
            cache_result.append(year)
            return tuple(cache_result)
        else:
            print(f"Loading 3d model: {path}")
            #Extra the batch and piece number from the path

            import time
            now = time.time()
            brightness_3d = list(main_presenter.get_brightnesses_3d(path))    
            
            (
                area,
                width_length_summary,
            ) = main_presenter.get_3d_object_area_and_width_length(path)
            
            #As area and width_length depend on the size of grid, which we have no control. We disable area and width_length in other parts of the code and here
           

            width_length_summary = list(width_length_summary)
            context = main_view.context_cb.currentText()
            zone = main_view.zone_cb.currentText()
            hemisphere = main_view.hemisphere_cb.currentText()
            utm_easting = main_view.easting_cb.currentText()
            utm_northing = main_view.northing_cb.currentText()
            
            contour = self.get_contour_3d(path)



            return_values = (batch_num, piece_num, brightness_3d,  width_length_summary, area, context, contour)

            main_model.cache_3d.set(path, return_values)
            return_values = list(return_values)
            return_values.append(year)
            return_values = tuple(return_values)
            return return_values


    def get_year_models(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()    
        all_model_paths = glob(str(main_presenter.get_context_dir() / main_model.path_variables["MODELS_FILES_DIR"]))
        if not all_model_paths:
            main_view.statusLabel.setText(f"No models were found")


        models_dict = dict()
        for path in all_model_paths:
            m = re.search(
                main_model.path_variables["MODELS_FILES_RE"], path.replace("\\", "/")
            )
            # This error happens when the relative path is different
            year = m.group(1)
           
            if year.isnumeric():
                year = int(year)
                batch_num = int(m.group(2))
                piece_num = int(m.group(3))
                if year in models_dict:
                    if batch_num in models_dict[year]:
                        if not (piece_num in  models_dict[year][batch_num]):
                            models_dict[year][batch_num][piece_num] = path
                    else:
                        models_dict[year][batch_num] = dict()
                        models_dict[year][batch_num][piece_num] = path
                else:
                    models_dict[year] = dict()
                    models_dict[year][batch_num] = dict()
                    models_dict[year][batch_num][piece_num] = path
        return models_dict
        # Sort the items
 


    def get_batched_models(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()    
        all_model_paths = glob(str(main_presenter.get_context_dir() / main_model.path_variables["MODELS_FILES_DIR"]))
        if not all_model_paths:
            main_view.statusLabel.setText(f"No models were found")


        batches_dict = dict()
        for path in all_model_paths:
            m = re.search(
                main_model.path_variables["MODELS_FILES_RE"], path.replace("\\", "/")
            )
            # This error happens when the relative path is different
            year = m.group(1)
             
            batch_num = m.group(2)
            piece_num = m.group(3)
            if batch_num not in batches_dict:
                batches_dict[batch_num] = [[int(piece_num), path, year]]
            else:
                batches_dict[batch_num].append([int(piece_num), path, year])

        # Sort the items

        for key in batches_dict:
            batches_dict[key] = sorted(batches_dict[key])
        return batches_dict
 
    def get_3d_model_info(self, current_item):
        batch_num = current_item["batch_num"]
        piece_num = current_item["piece_num"]
        brightness_3d = current_item["brightness_summary"]
        width_length_summary = current_item["width_length_summary"]
        area = current_item["area"]
        
        context = current_item["context"]
       
        return (
            batch_num,
            piece_num,
            brightness_3d,
            width_length_summary,
            area,
        
            context,
            
        )

    def get_matched_plys(self, _3d_model_dict):
        all_matched_3d_models = set()
        for key in _3d_model_dict:
            if not (_3d_model_dict[key][0] == None and _3d_model_dict[key][1] == None):
                all_matched_3d_models.add(_3d_model_dict[key])
        return all_matched_3d_models

 