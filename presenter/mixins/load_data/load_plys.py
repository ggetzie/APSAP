from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)
from glob import glob


class LoadPlys:

    def populate_models(self):
        """This is one of the two functions in the whole application that populate 3d models into the list.
        This function populates the list that not sorted by similarity but by year, batch then piece number
        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        # We block interactions with the GUI during loading!
        main_view.blockSignals(True)
 
        # Either create a model for the selection model instance, or remove all the rows in it
        self.reset_ply_selection_model()

        # A tree like structure where you can get use tree traveral using a dict to get all the 3d models
        #First by their year, then by their batch, then finally by their piece number
        #We use this tree like structure to make sure things run in O(n)
        years_models = self.get_year_models()

        # We go through each record year
        for batch_year in sorted(years_models.keys()):
            #If the year is not the year set by current filter, we ignore this year
            if int(batch_year) != int(main_view.year.value()):
                continue

            #If the year matches the current year, we go through the batches
            #The year_item will store the batch_items in it
            year_item = QStandardItem(f"{batch_year}")
            for batch in sorted(years_models[batch_year].keys()):
                #If the batch is out of the filter, we ignore the batch
                if int(batch) < int(main_view.batch_start.value()) or int(batch) > int(
                    main_view.batch_end.value()
                ):
                    continue

                #If the batch is within the filter, we go through the pieces in the batch
                #The batch_item will store the piece_items in it

                batch_item = QStandardItem(f"{batch}")
                for batch_piece in sorted(years_models[batch_year][batch].keys()):
                    #We get the path to the 3d model
                    path = years_models[batch_year][batch][batch_piece]

                    #We measure the 3d model in the path to precache the value
                    main_presenter.measure_pixels_3d(path)
                    #We set the modelPiece item that will be appened to the modelPiece item
                    modelPiece = QStandardItem(f"{batch_piece}")
                    #Remember to store the path in the item
                    modelPiece.setData(f"{path}", Qt.UserRole)

                    #Set the item as red in case the piece is matched to a find already
                    ply_str = f"{int(batch_year)},{int(batch)},{int(batch_piece)}"
                    if ply_str in main_view.dict_ply_2_find:
                        modelPiece.setForeground(QColor("red"))
                    
                    #Add the piece item to the batch item
                    batch_item.appendRow(modelPiece)

                #Add the batch item to the year item
                year_item.appendRow(batch_item)

            #Add the year_item to the whole select
            main_view.modelList.selectionModel().model().appendRow(year_item)


        #After loading is successful, we enable the interactions with the GUI.
        main_view.blockSignals(False)

    def reset_ply_selection_model(self):
        """This function ensures that there is a empty modelList
        in the view
        """         
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        #We create a new modelList's selection model if there isn't one
        if not main_view.modelList.selectionModel():
            model = QStandardItemModel(main_view)
            model.setHorizontalHeaderLabels(["Models"])
            main_view.modelList.setModel(model)
            main_view.modelList.selectionModel().currentChanged.connect(
                main_presenter.change_3d_model
            )
        else:
        #Otherwise we empty the list
            main_view.modelList.selectionModel().model().removeRows(
                0, main_view.modelList.selectionModel().model().rowCount()
            )

    def get_year_models(self):
        """This function generate trees that represent the 3d model.
        The trees consist of four layers

        Layer 0:
            Year: 2022, 2021
        Layer 1:
            Batch: 001, 002
        Layer 2:
            Piece: 1, 2
        Layer 3:
            Path: whole path to the 3d model
            

        Returns:
            dict: A dictionary of years as keys. Dictionaries are nested in dictionaries. You can see them as trees
        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        #Get all the 3d models in the current path
        all_model_paths = glob(
            str(
                main_presenter.get_context_dir()
                / main_model.path_variables["MODELS_FILES_DIR"]
            )
        )

        #Notify in the GUI if there are no 3d models
        if not all_model_paths:
            main_view.statusLabel.setText(f"No models were found")
            main_view.statusLabel.repaint()

        models_dict = dict()
        #Go through each path, and add them to as a tree structure using Python Dict()
 
        for path in all_model_paths:
            (year, batch, piece) = main_presenter.get_year_batch_piece(path)
            #We ignore the folder if not all three pieces of info are not null
            if year == None or batch == None or piece == None:
                continue
            #We also ignore the folder if the year is not numeric
            if not year.isnumeric():
                continue

            #These three if statements will try to see if the current path has portion of it
            #Already added before.  
            #E.g. We previously added 2022, 001, 03
            #This is a dictionary with 2022 as a key, pointing to another dictionary with 001 as the key,
            #poting to another dictionary with 03 as the key,..abs
            #Now if we have 2022, 001, 02, we merely add 02 to the dicionary pointed by 001
            if not year in models_dict:
                models_dict[year] = dict()
            if not batch in models_dict[year]:
                models_dict[year][batch] = dict()
            if not (piece in models_dict[year][batch]):
                models_dict[year][batch][piece] = path

        return models_dict
