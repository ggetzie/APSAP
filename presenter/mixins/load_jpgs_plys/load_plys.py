 
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
        self.reset_ply_measurements()
    
        #models of the current folder are grouped by batches they belong to
        batched_models = self.get_batched_models()

        #We must know the 3d models that were matched with a pair of jpgs, 
        matched_plys = self.get_matched_plys(main_view._3d_model_dict)

        #Go through each batch
        for batch in batched_models:
           
            model_batch = QStandardItem(f"{batch}")
            pieces = batched_models[batch]
            #Go through each piece of the current batch
            for piece in pieces:
                piece_num = piece[0]
                path = piece[1]
               
                #Either calculaute the info of the ply file or get it form cache
                (batch_num, piece_num, brightness_3d, width_length_summary, area,   context) = self.load_ply_info_from_cache_or_calc(path)
              
                #Add all thosecalculuated data of rhe current piece into the lists so that it can, later, be used for similarity calculuation
                main_view.areas_3d.append([area, batch_num, piece_num])
                main_view.brightnesses_3d.append([brightness_3d, batch_num, piece_num])
                main_view.width_lengths_3d.append([width_length_summary, batch_num, piece_num])
               
                #Create a piece q item later for use
                modelPiece = QStandardItem(f"{piece_num}")
                modelPiece.setData(f"{path}", Qt.UserRole)
               
                #Set the color of the item to be red if it already had a match before
                if (int(batch_num), int(piece_num)) in matched_plys:
                    modelPiece.setForeground(QColor("red"))
               
               
                model_batch.appendRow(modelPiece)
           
           
            main_view.modelList.selectionModel().model().appendRow(model_batch)
       
    
        main_model.simple_save_json(main_model.json_data, "./configs/cache.json")
 
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


 
    def load_ply_info_from_cache_or_calc(self, path):

        main_model, main_view, main_presenter = self.get_model_view_presenter()    
        #If we have the data in cache, we don't need to calculuate it
        if path in main_model.path_info_dict:
            print(path)
            current_item = main_model.path_info_dict[path]
            (
                batch_num, piece_num, brightness_3d, 
                width_length_summary, area,  context
            ) = self.get_3d_model_info(current_item)

        #calculuate the data of the ply, also saves it in to the json object
        else:
            print(f"Loading 3d model: {path}")
            #Extra the batch and piece number from the path
            m = re.search(
                    main_model.path_variables["MODELS_FILES_RE"],
                path.replace("\\", "/"),
            )
            
            batch_num = m.group(1)
            piece_num = m.group(2)
            import time
            now = time.time()
            brightness_3d = list(main_presenter.get_brightnesses_3d(path))    
         
            (
                area,
                width_length_summary,
            ) = main_presenter.get_3d_object_area_and_width_length(path)
 
            

            width_length_summary = list(width_length_summary)
            context = main_view.context_cb.currentText()
            zone = main_view.zone_cb.currentText()
            hemisphere = main_view.hemisphere_cb.currentText()
            utm_easting = main_view.easting_cb.currentText()
            utm_northing = main_view.northing_cb.currentText()
            
            temp = {
                "path": path,  "batch_num": batch_num, "piece_num": piece_num,
                 "brightness_summary": brightness_3d,
                  "area": area, "width_length_summary": width_length_summary,
                "context":context, "zone":zone, "hemisphere": hemisphere, "utm_easting": utm_easting,"utm_northing": utm_northing
            }
    

            main_model.json_data["past_records"].append(temp)

        return (batch_num, piece_num, brightness_3d,  width_length_summary, area, context)




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
            batch_num = m.group(1)
            piece_num = m.group(2)
            if batch_num not in batches_dict:
                batches_dict[batch_num] = [[int(piece_num), path]]
            else:
                batches_dict[batch_num].append([int(piece_num), path])

        # Sort the items

        for key in batches_dict:
            batches_dict[key] = sorted(batches_dict[key])
        return batches_dict


    def reset_ply_measurements(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()    

        main_view.areas_3d = []
        main_view.brightnesses_3d = []
        main_view.width_lengths_3d = []

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

 