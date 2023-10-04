from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QColor 
from pathlib import Path
import logging
class LoadFinds:

    def populate_finds(self):
        """This function adds all the finds onto the finds list
        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        main_presenter.blockSignals(True)

        #Get all the finds and sort them by their numerical values
        context_dir = main_presenter.get_context_dir()
        finds_dir = context_dir / main_model.path_variables["FINDS_SUBDIR"]
        finds = main_presenter.get_options(finds_dir)
        finds.sort(key=lambda f: int(f))

        # Get a dictionary to get the mapping between plys and finds if they are already matched
        main_view.dict_find_2_ply = dict()
        main_view.dict_ply_2_find = dict()

        # Get all the path elements necessary to reconstruct the image paths.
        easting, northing, context = main_presenter.get_easting_northing_context()
        finds_subdir = main_model.path_variables["FINDS_SUBDIR"]
        finds_photo_dir = main_model.path_variables["FINDS_PHOTO_DIR"]


        duplicates_checks = dict()

        #Go through all finds one by one
        for find in finds:
            #Setting the base path to the find
            find_base_path = context_dir / finds_subdir / find / finds_photo_dir

            #Updating on the GUI to show that we are loading this find
            logging.info(f"Loading the folder: {find_base_path}")  
            main_view.statusLabel.setText(f"Loading find in folder {find_base_path}")
            main_view.statusLabel.repaint()

            #Check if the two jpeg files exist.
            if not (Path(find_base_path / "1.jpg").is_file() and Path(find_base_path / "2.jpg").is_file() ) :
                continue
 
            #Check if the find number is within the filter range
            if  int(find) < int(main_view.find_start.value()) or int(find) > int(main_view.find_end.value()):
                continue
            #Create a QListWidgetitem of the find to be added to the find
            item = QListWidgetItem(find)

            #We want to check if this find has already be matched before
            #If yes, 
            # We set the item as red to indicate it is matched already
            # We also store the matching result in two dict() so we can later reference it
            (batch_year, batch_num, batch_piece) = main_model.get_sherd_info(easting, northing, context, find)    
            if batch_year!= None  and batch_num!=None and batch_piece!=None:
                text = f"{easting},{northing},{context},{batch_year},{batch_num},{batch_piece}"
                if text not in duplicates_checks:
                    duplicates_checks[text] = [find]
                else:
                    duplicates_checks[text].append(find)
        
                item.setForeground(QColor("red"))
                find_str = f"{easting},{northing},{context},{int(find)}"
                ply_str = f"{int(batch_year)},{int(batch_num)},{int(batch_piece)}"
                main_view.dict_find_2_ply[find_str] = ply_str
                main_view.dict_ply_2_find[ply_str] = find_str
            #Finally we add our item to the list
            main_view.finds_list.addItem(item)
        logging.info(f"Showing possible duplicates")  
        for key in duplicates_checks:
            if (len(duplicates_checks[key]) >= 2):
                logging.info(f"Duplicates: ")
                logging.info(f"Key: {key}")  
                logging.info(f"find: {duplicates_checks[key]}")  

            
        main_presenter.blockSignals(False)
        