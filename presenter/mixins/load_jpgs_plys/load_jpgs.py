 
from PyQt5.QtWidgets import (
    QListWidgetItem,
)
from PyQt5.QtGui import QColor 
from pathlib import Path
class LoadJpgs:


    def get_find_of_a_ply(self, batch_num, batch_piece, batch_year):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        ply_str = f"{int(batch_year)},{int(batch_num)},{int(batch_piece)}"
        if main_view.dict_ply_2_find and ply_str in main_view.dict_ply_2_find:
            return main_view.dict_ply_2_find[ply_str]
        else:
            return None
        
    def get_ply_of_a_find(easting, northing, context, find):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        find_str = f"{easting},{northing},{context},{int(find)}"
        if main_view.dict_find_2_ply and find_str in main_view.dict_find_2_ply:
            return main_view.dict_find_2_ply[find_str]
        else:
            return None
         

    def populate_finds(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        main_view.finds_list.clear()

        context_dir = main_presenter.get_context_dir()
        finds_dir = context_dir / main_model.path_variables["FINDS_SUBDIR"]
        finds = main_presenter.get_options(finds_dir)
        # Getting easting, northing and context for getting doing the query
        finds.sort(key=lambda f: int(f))

        # Get a dictionary to get all
        main_view._3d_model_dict = dict()
        main_view.dict_find_2_ply = dict()
        main_view.dict_ply_2_find = dict()
        easting, northing, context = main_presenter.get_easting_northing_context()
        finds_subdir = main_model.path_variables["FINDS_SUBDIR"]
        finds_photo_dir = main_model.path_variables["FINDS_PHOTO_DIR"]

        #Testing if all the years are 2022
        #D:\ararat\data\files\N\38\483390\4419290\9\finds\individual

        for find in finds:
            jpg_1_path = context_dir / finds_subdir / find / finds_photo_dir / "1.jpg"
            jpg_2_path = context_dir / finds_subdir / find / finds_photo_dir / "2.jpg"

            if Path(jpg_1_path).is_file() and Path(jpg_2_path).is_file():
                print(f"Loading the folder: {context_dir / finds_subdir / find / finds_photo_dir }")
                item = QListWidgetItem(find)
                batch_num, batch_piece, batch_year = main_model.get_sherd_info(easting, northing, context, int(find))                # print(f"The year we get from DB is: {_3d_locations[2]}")
                #_3d_locations[0] is batch, _3d_locations[1] is piece
                main_view._3d_model_dict[f"{easting},{northing},{context},{int(find)}"] =  (batch_num, batch_piece)  
                if batch_year!= None  and batch_num!=None and batch_piece!=None:
                    item.setForeground(QColor("red"))
                    find_str = f"{easting},{northing},{context},{int(find)}"
                    ply_str = f"{int(batch_year)},{int(batch_num)},{int(batch_piece)}"
                    main_view.dict_find_2_ply[find_str] = ply_str
                    main_view.dict_ply_2_find[ply_str] = find_str
                main_view.finds_list.addItem(item)
