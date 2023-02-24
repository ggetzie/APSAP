 
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
        """
            A rather long function that simply put all the 3d models in the list.
        """
        #Step 1: Get some variables to be used throughout the function
        main_model, main_view, main_presenter = self.get_model_view_presenter()    

        if main_view.context_cb.count() > 0:    
            models_files_dir = main_model.path_variables["MODELS_FILES_DIR"]
            models_files_re = main_model.path_variables["MODELS_FILES_RE"]

            #Step 2: Check get all models from the path. If there are no paths, say it in the status label
            all_model_paths = glob(str(main_presenter.get_context_dir() / models_files_dir))
            if not all_model_paths:
                main_view.statusLabel.setText(f"No models were found")

            #Step 3: Crate a dictionary whose key is the batch number and whose value is list of the model within that batch
            batches_dict = self.get_batched_models(all_model_paths)

            #Step 4: Get all 3d models already matched, so that in the items in the list, we can redden those that aalready matched
            all_matched_3d_models = self.get_matched_3d_models(main_view._3d_model_dict)

            #Step 5: We create a Q model that stores the 3d models 
            
            if not main_view.modelList.selectionModel():
                model = QStandardItemModel(main_view)
                model.setHorizontalHeaderLabels(["Models"])
                main_view.modelList.setModel(model)
                main_view.modelList.selectionModel().currentChanged.connect(main_presenter.change_3d_model)
            else:
                main_view.modelList.selectionModel().model().removeRows(0, main_view.modelList.selectionModel().model().rowCount())

                #print(   main_view.modelList.selectionModel())
                #print(   main_view.modelList.selectionModel().model())
            
            model = main_view.modelList.selectionModel().model()
            #Step 6: These lists contains the info bundled with the batch and piece number so that when the similiarity calculation hits we have the info to compare
            main_view.areas_3d = []
            main_view.brightnesses_3d = []
            main_view.colors_3d = []
            main_view.width_lengths_3d = []
            main_view.circle_ratios_3d = []

            #Step 7: (1)For each batch in the batches,
            for batch in batches_dict:
                items = batches_dict[batch]
                model_batch = QStandardItem(f"{batch}")
                #(2)For each item in each batch,
                for item in items:
                    index = item[0]
                    path = item[1]
                    #(3)We first consider whether we have already get the information before, if yes, we can just extract the information from the item
                    if path in main_model.path_info_dict:
                        current_item = main_model.path_info_dict[path]
                        (
                            batch_num, piece_num, brightness_3d, colors_summary,
                            width_length_summary, area, index, context, cirlcle_area_ratio,
                        ) = self.get_3d_model_info(current_item)

                    #(4)If we dont have the information yet, we have to calculate it ourselves, we also need to save the calcuated data into the json_data, past_records, so that we don't have to recalculuate it next time.
                    else:
                        print(f"Loading 3d model: {path}")
                        #Extra the batch and piece number from the path
                        m = re.search(
                            models_files_re,
                            path.replace("\\", "/"),
                        )
                        
                        batch_num = m.group(1)
                        piece_num = m.group(2)

                    
                        brightness_3d = list(main_presenter.get_brightnesses_3d(path))                
                        colors_summary = list(main_presenter.get_color_summary_from_3d(path))
                        (
                            area,
                            width_length_summary,
                        ) = main_presenter.get_3d_object_area_and_width_length(path)

                        cirlcle_area_ratio = main_presenter.get_3d_area_circle_ratio(path)
                        width_length_summary = list(width_length_summary)
                        context = main_view.context_cb.currentText()
                        zone = main_view.zone_cb.currentText()
                        hemisphere = main_view.hemisphere_cb.currentText()
                        utm_easting = main_view.easting_cb.currentText()
                        utm_northing = main_view.northing_cb.currentText()
                        #Storing the data into an dict
                        temp = {
                            "path": path, "index": index, "batch_num": batch_num, "piece_num": piece_num,
                            "cirlcle_area_ratio": cirlcle_area_ratio, "brightness_summary": brightness_3d,
                            "colors_summary" : colors_summary, "area": area, "width_length_summary": width_length_summary,
                            "context":context, "zone":zone, "hemisphere": hemisphere, "utm_easting": utm_easting,"utm_northing": utm_northing
                        }
                
        
                        main_model.json_data["past_records"].append(temp)
                    
                    #After we get all the information for this item, we can now add it into the list along with the batch number and piece number
                    main_view.colors_3d.append(colors_summary)    
                    main_view.circle_ratios_3d.append([cirlcle_area_ratio, batch_num, piece_num])
                    main_view.areas_3d.append([area, batch_num, piece_num])
                    main_view.brightnesses_3d.append([brightness_3d, batch_num, piece_num])
                    main_view. width_lengths_3d.append([width_length_summary, batch_num, piece_num])

                    modelPiece = QStandardItem(f"{index}")
                    modelPiece.setData(f"{path}", Qt.UserRole)
                    if (int(batch_num), int(piece_num)) in all_matched_3d_models:
                        modelPiece.setForeground(QColor("red"))
                    model_batch.appendRow(modelPiece)
                model.appendRow(model_batch)

            #main_view.modelList.setModel(model)
            #main_view.modelList.selectionModel().currentChanged.connect(main_presenter.change_3d_model)

            main_model.simple_save_json(main_model.json_data, "./configs/cache.json")

    
    def get_3d_model_info(self, current_item):
        batch_num = current_item["batch_num"]
        piece_num = current_item["piece_num"]
        brightness_3d = current_item["brightness_summary"]
        colors_summary = current_item["colors_summary"]
        width_length_summary = current_item["width_length_summary"]
        area = current_item["area"]
        index = current_item["index"]
        context = current_item["context"]
        cirlcle_area_ratio = current_item["cirlcle_area_ratio"]
        return (
            batch_num,
            piece_num,
            brightness_3d,
            colors_summary,
            width_length_summary,
            area,
            index,
            context,
            cirlcle_area_ratio,
        )

    def get_matched_3d_models(self, _3d_model_dict):
        all_matched_3d_models = set()
        for key in _3d_model_dict:
            if not (_3d_model_dict[key][0] == None and _3d_model_dict[key][1] == None):
                all_matched_3d_models.add(_3d_model_dict[key])
        return all_matched_3d_models

    def get_batched_models(self, all_model_paths):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

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
