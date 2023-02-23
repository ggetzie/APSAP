 
from PyQt5.QtWidgets import (
    QListWidgetItem,
)
from PyQt5.QtGui import QColor 
from pathlib import Path

class LoadJpgs:


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
        easting, northing, context = main_presenter.get_easting_northing_context()
        finds_subdir = main_model.path_variables["FINDS_SUBDIR"]
        finds_photo_dir = main_model.path_variables["FINDS_PHOTO_DIR"]
        for find in finds:

            jpg_1_path = context_dir / finds_subdir / find / finds_photo_dir / "1.jpg"
            jpg_2_path = context_dir / finds_subdir / find / finds_photo_dir / "2.jpg"

            if Path(jpg_1_path).is_file() and Path(jpg_2_path).is_file():

                item = QListWidgetItem(find)
                _3d_locations = main_model.get_sherd_info(easting, northing, context, int(find))

                if _3d_locations[0] != None and _3d_locations[1] != None:
                    item.setForeground(QColor("red"))
                main_view.finds_list.addItem(item)
                main_view._3d_model_dict[f"{easting},{northing},{context},{int(find)}"] = _3d_locations