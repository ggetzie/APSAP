 
         
from PyQt5.QtCore import Qt, QCoreApplication


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
        main_presenter.blockSignals(True)

        # Qt associates a model with a select object. 
        self.reset_ply_selection_model()

        # Get a tree like structure that stores all the ply.
        years_models = (self.get_year_models())


        
        for batch_year in sorted(years_models.keys()):
            if int(batch_year) !=int( main_view.year.value()):
                continue
            year_item = QStandardItem(f"{batch_year}")
            for batch in sorted(years_models[batch_year].keys()):
                if int(batch) < int(main_view.batch_start.value()) or int(batch) > int(main_view.batch_end.value()):
                    continue
                batch_item =  QStandardItem(f"{batch}")
                for batch_piece in sorted(years_models[batch_year][batch].keys()):
                   path =  years_models[batch_year][batch][batch_piece]
                   main_presenter.measure_pixels_3d(path)
                   modelPiece = QStandardItem(f"{batch_piece}")
                   modelPiece.setData(f"{path}", Qt.UserRole)

                   ply_str = f"{int(batch_year)},{int(batch)},{int(batch_piece)}"
 
                   if ply_str in main_view.dict_ply_2_find   :
                        modelPiece.setForeground(QColor("red"))
                   batch_item.appendRow(modelPiece)
                year_item.appendRow(batch_item)
            main_view.modelList.selectionModel().model().appendRow(year_item)
        main_presenter.blockSignals(False)


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


 


    def get_year_models(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()    
        all_model_paths = glob(str(main_presenter.get_context_dir() / main_model.path_variables["MODELS_FILES_DIR"]))
        if not all_model_paths:
             
            main_view.statusLabel.setText(f"No models were found")
            main_view.statusLabel.repaint()
           
        models_dict = dict()
        for path in all_model_paths:
            (year, batch, piece) =  main_presenter.get_year_batch_piece(path)
            if year == None or batch == None or piece == None:
                continue
            if not year.isnumeric():
                continue

            if not year in models_dict:
                models_dict[year] = dict()
            if not batch in models_dict[year]:
                models_dict[year][batch] = dict()
            if not (piece in models_dict[year][batch]):
                models_dict[year][batch][piece] = path

                
             
                
        return models_dict
        # Sort the items
 