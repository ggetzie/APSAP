import sys
opengl_path = 'E:\\Users\\bertliu\\Downloads\\opengl32.dll'

import ctypes
import scipy.optimize as opt
ctypes.cdll.LoadLibrary(opengl_path)
from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import (
    QColor,
    QIcon,
    QPixmap,
    QImage,
    QWindow,
    QStandardItem,
    QStandardItemModel,
    QMovie,
    QPainter,
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QListWidgetItem,
    QFileDialog,
    QMessageBox,
    QSplashScreen,
)

import pathlib
import open3d as o3d
import re
from database_tools import get_pottery_sherd_info, update_match_info
from glob import glob as glob
from database_tools import get_all_pottery_sherd_info
from components.debug_funcs import DebugFuncs
import json
import numpy as np
import time
basedir = pathlib.Path().resolve()
from components.vis import Visualized
from components.pop_up import PopUp
from components.load_qt_images_models import LoadImagesModels
from misc import simple_get_json, simple_save_json
FINDS_SUBDIR = "finds/individual"
BATCH_3D_SUBDIR = "finds/3dbatch"
FINDS_PHOTO_DIR = "photos"
MODELS_FILES_DIR = "finds/3dbatch/2022/batch_*/registration_reso1_maskthres242/final_output/piece_*_world.ply"
MODELS_FILES_RE = "finds/3dbatch/2022/batch_(.+?)/registration_reso1_maskthres242/final_output/piece_(.+?)_world.ply"
HEMISPHERES = ("N", "S")



# Here let's do some simple machine learning to get


class MainWindow(QMainWindow, PopUp, Visualized, LoadImagesModels, DebugFuncs):
    """View (GUI)."""

    def __init__(self):
        """View initializer."""
        super(MainWindow, self).__init__()

        uic.loadUi("qtcreator/MainWindow.ui", self)
        if not self.check_has_path_in_setting():
            self.ask_for_prompt()
        
        setting = json.load(open("settings.json"))
        self.json_data = simple_get_json("data.json")
        self.parameters = simple_get_json("parameters.json")
        calculuated_paths = dict()
        for obj in self.json_data["past_records"]:
            calculuated_paths[obj["path"]] = obj
        self.calculuated_paths = calculuated_paths
        self.file_root = pathlib.Path(setting["FILE_ROOT"] )
 

        self.set_up_3d_window()
        self.populate_hemispheres()

        self.hemisphere_cb.currentIndexChanged.connect(self.populate_zones)
        self.zone_cb.currentIndexChanged.connect(self.populate_eastings)
        self.easting_cb.currentIndexChanged.connect(self.populate_northings)
        self.northing_cb.currentIndexChanged.connect(self.populate_contexts)
        self.context_cb.currentIndexChanged.connect(self.contextChanged)
        self.contextDisplay.setText(self.get_context_string())

        self.findsList.currentItemChanged.connect(self.load_find_images)

        self.update_button.clicked.connect(self.update_model_db)
        self.remove_button.clicked.connect(self.adjusting_similaritiy_weights)


  
    def populate_hemispheres(self):
        self.hemisphere_cb.clear()
        res = [
            d.name
            for d in self.file_root.iterdir()
            if d.name in HEMISPHERES and d.is_dir()
        ]
        self.hemisphere_cb.addItems(res)
        self.set_hemisphere(0 if len(res) > 0 else -1)
        self.hemisphere_cb.setEnabled(len(res) > 1)
        self.contextDisplay.setText(self.get_context_string())

    def set_hemisphere(self, index):
        self.hemisphere_cb.setCurrentIndex(index)
        self.populate_zones()

    def populate_zones(self):
        self.zone_cb.clear()
        hemisphere = self.hemisphere_cb.currentText()
        zone_root = self.file_root / hemisphere
        res = [d.name for d in zone_root.iterdir() if d.is_dir() and d.name.isdigit()]
        self.zone_cb.addItems(res)
        self.zone_cb.setEnabled(len(res) > 1)
        self.set_zone(0 if len(res) > 0 else -1)

    def set_zone(self, index):
        self.zone_cb.setCurrentIndex(index)
        self.populate_eastings()

    def populate_eastings(self):
        self.easting_cb.clear()
        hemisphere = self.hemisphere_cb.currentText()
        zone = self.zone_cb.currentText()
        eastings_root = self.file_root / hemisphere / zone
        res = [
            d.name for d in eastings_root.iterdir() if d.is_dir() and d.name.isdigit()
        ]
        self.easting_cb.addItems(res)
        self.set_easting(0 if len(res) > 0 else -1)
        self.easting_cb.setEnabled(len(res) > 1)

    def set_easting(self, index):
        self.easting_cb.setCurrentIndex(index)
        self.populate_northings()

    def populate_northings(self):
        self.northing_cb.clear()
        northings_root = (
            self.file_root
            / self.hemisphere_cb.currentText()
            / self.zone_cb.currentText()
            / self.easting_cb.currentText()
        )
        res = [
            d.name for d in northings_root.iterdir() if d.is_dir() and d.name.isdigit()
        ]
        self.northing_cb.addItems(res)
        self.set_northing(0 if len(res) > 0 else -1)
        self.northing_cb.setEnabled(len(res) > 1)

    def set_northing(self, index):
        self.northing_cb.setCurrentIndex(index)
        self.populate_contexts()

    def populate_contexts(self):
        self.context_cb.clear()
        contexts_root = (
            self.file_root
            / self.hemisphere_cb.currentText()
            / self.zone_cb.currentText()
            / self.easting_cb.currentText()
            / self.northing_cb.currentText()
        )
        res = [
            d.name for d in contexts_root.iterdir() if d.is_dir() and d.name.isdigit()
        ]
        self.context_cb.addItems(res)
        self.set_context(0 if len(res) > 0 else -1)
        self.context_cb.setEnabled(len(res) > 1)

        funcs_to_run = [
            ["Loading finds. It might take a while", self.populate_finds],
            ["Loading models. It might take a while", self.populate_models],
        ]
        self.load_and_run(funcs_to_run)

    def set_context(self, index):
        self.context_cb.setCurrentIndex(index)

    def get_context_string(self):
        """Return a string representing the full designation of the current context
        as utm_hemisphere-utm_zone-utm_easting-utm_northing-context_number

        Returns:
            str: The full designation of the currently selected context
        """
        hzenc = [
            self.hemisphere_cb.currentText(),
            self.zone_cb.currentText(),
            self.easting_cb.currentText(),
            self.northing_cb.currentText(),
            self.context_cb.currentText(),
        ]
        return "-".join(hzenc)

    def get_context_dir(self):
        res = (
            self.file_root
            / self.hemisphere_cb.currentText()
            / self.zone_cb.currentText()
            / self.easting_cb.currentText()
            / self.northing_cb.currentText()
            / self.context_cb.currentText()
        )
        if not res.exists():
            self.statusLabel.setText(f"{res} does not exist!")
            return pathlib.Path()
        return res

    def get_easting_northing_context(self):
        context_dir = self.get_context_dir()
        path_parts = pathlib.Path(context_dir).parts[-3:]
        easting = int(path_parts[0])
        northing = int(path_parts[1])
        context = int(path_parts[2])
        return (easting, northing, context)

    def contextChanged(self):
        self.statusLabel.setText(f"")
        self.selected_find.setText(f"")
        self.current_batch.setText(f"")
        self.current_piece.setText(f"")
        self.new_batch.setText(f"")
        self.new_piece.setText(f"")
        self.contextDisplay.setText(self.get_context_string())
        if hasattr(self, "current_pcd"):
            self.vis.remove_geometry(self.current_pcd)
            self.current_pcd = None

        model = QStandardItemModel(self)
        self.sortedModelList.setModel(model)
        funcs_to_run = [
            ["Loading finds. It might take a while", self.populate_finds],
            ["Loading models. It might take a while", self.populate_models],
        ]
        import time

        now = time.time()
        self.load_and_run(funcs_to_run)
        print(f"Timed passed: {time.time() - now} seconds")

    def populate_finds(self):
        # if self.splash:
        #    self.splash.showMessage("Loading finds")
        self.findsList.clear()
        context_dir = self.get_context_dir()
 
        finds_dir = context_dir / FINDS_SUBDIR
        finds = [d.name for d in finds_dir.iterdir() if d.name.isdigit()]
        # Getting easting, northing and context for getting doing the query
        easting_northing_context = self.get_easting_northing_context()
        finds.sort(key=lambda f: int(f))

        # Get a dictionary to get all
        self._3d_model_dict = dict()
        for find in finds:
             
            first_jpg_path = self.get_context_dir() / FINDS_SUBDIR / find / FINDS_PHOTO_DIR / "1.jpg"
            second_jpg_path = self.get_context_dir() / FINDS_SUBDIR / find / FINDS_PHOTO_DIR / "2.jpg"
             
            if pathlib.Path(first_jpg_path).is_file() and pathlib.Path(second_jpg_path).is_file:

                item = QListWidgetItem(find)
                _3d_locations = get_pottery_sherd_info(
                    easting_northing_context[0],
                    easting_northing_context[1],
                    easting_northing_context[2],
                    int(find),
                )

                if _3d_locations[0] != None and _3d_locations[1] != None:
                    item.setForeground(QColor("red"))
                self.findsList.addItem(item)
                self._3d_model_dict[
                    f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find)}"
                ] = _3d_locations

    def populate_models(self):
        # Populate all models and at the same time get the information of those models for comparison.

        path = str((self.get_context_dir() / MODELS_FILES_DIR))
        all_model_paths = glob(path)
        
         
        if not all_model_paths:
            self.statusLabel.setText(f"No models were found")
        # Setting up the model
        model = QStandardItemModel(self)
        model.setHorizontalHeaderLabels(["Models"])
        # Getting a dict for all the batches
        batches_dict = dict()
        for path in all_model_paths:
            m = re.search(MODELS_FILES_RE, path.replace("\\", "/"))
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

        all_matched_3d_models = set()

        for key in self._3d_model_dict:
            if not (
                self._3d_model_dict[key][0] == None
                and self._3d_model_dict[key][1] == None
            ):
                all_matched_3d_models.add(self._3d_model_dict[key])

        # Add all items onto the QTree

        # We get all the information of all the 3d models, that we can use to rank them by similarity
        actual_index = 0
        all_3d_areas = []
        all_3d_brightness_summaries = []
        all_3d_colors_summaries = []
        all_3d_width_length_summaries = []
        import time

        now = time.time()
        for batch in batches_dict:
            items = batches_dict[batch]
            batch = QStandardItem(f"{batch}")

            for item in items:
                index = item[0]
                 
                path = item[1]
                
                if path in self.calculuated_paths:
                    batch_num = self.calculuated_paths[path]["batch_num"]
                    piece_num = self.calculuated_paths[path]["piece_num"]
                    brightness_summary = self.calculuated_paths[path]["brightness_summary"]
                    colors_summary = self.calculuated_paths[path]["colors_summary"]
                    width_length_summary = self.calculuated_paths[path]["width_length_summary"]
                    area = self.calculuated_paths[path]["area"]
                    index = self.calculuated_paths[path]["index"]    
                    context =  self.calculuated_paths[path]["context"]
 

                else:

                    m = re.search(MODELS_FILES_RE, path.replace("\\", "/"))
                    # This error happens when the relative path is different
                    batch_num = m.group(1)
                    piece_num = m.group(2)

                    # Calculate the area of the current piece

                    brightness_summary = self.comparator.get_brightness_summary_from_3d(
                        path
                    )
                    brightness_summary = list(brightness_summary)
                
                    # Calculate the color summary of the current piece
                    colors_summary = self.comparator.get_color_summary_from_3d(path)
                    colors_summary = list(colors_summary)
                    (
                        area,
                        width_length_summary,
                    ) = self.comparator.get_3d_object_area_and_width_length(path)
                    width_length_summary = list(width_length_summary)
                    json_data = self.json_data
                    temp = {}
                    temp["path"] = path
                    temp["index"] = index
                    temp["batch_num"] = batch_num
                    temp["piece_num"] = piece_num
                    
                    temp["brightness_summary"] = brightness_summary
                    temp["colors_summary"] =  colors_summary
                    temp["area"] =  area
                    temp["width_length_summary"] =  width_length_summary
                    temp["context"] =  self.context_cb.currentText()
                    temp["zone"] = self.zone_cb.currentText()
                    temp['hemisphere'] = self.hemisphere_cb.currentText()
                    temp["utm_easting"] = self.easting_cb.currentText()
                    temp["utm_northing"] = self.northing_cb.currentText()

                    json_data["past_records"].append(temp)
                all_3d_colors_summaries.append(colors_summary)
                print(f"index: {actual_index}: 3dArea: {area}")

                 
                #Here we better save the information
                all_3d_areas.append([area, batch_num, piece_num])
                all_3d_brightness_summaries.append(
                    [brightness_summary, batch_num, piece_num]
                )
                all_3d_width_length_summaries.append(
                    [width_length_summary, batch_num, piece_num]
                )
                ply = QStandardItem(f"{index}")
                ply.setData(f"{path}", Qt.UserRole)
                if (int(batch_num), int(piece_num)) in all_matched_3d_models:
                    ply.setForeground(QColor("red"))
                batch.appendRow(ply)
                actual_index += 1
            model.appendRow(batch)
        simple_save_json(self.json_data, "data.json")

        print(f"{time.time() - now} seconds")
        self.all_3d_areas = all_3d_areas
        self.all_3d_width_length_summaries = all_3d_width_length_summaries
        self.all_3d_brightness_summaries = all_3d_brightness_summaries
        self.all_3d_colors_summaries = all_3d_colors_summaries
        self.modelList.setModel(model)
        self.modelList.selectionModel().currentChanged.connect(self.change_3d_model)

    def remove_match(self):
        # This functions removes the match between the image and the 3d model
        selected_item = self.findsList.currentItem()

        # Only remove model when an image is selected
        if selected_item:
            num = selected_item.text()
            selected_item.setForeground(QColor("black"))
            # Update the database
            easting, northing, context = self.get_easting_northing_context()
            update_match_info(easting, northing, context, num, None, None)
            # Unred the matched items in the 3d models list
            previous_current_batch_num = self.current_batch.text()
            previous_current_piece_num = self.current_piece.text()

            mod = self.modelList.model()
            # Make the item Black in modelList
            for i in range(mod.rowCount()):
                for j in range(mod.item(i).rowCount()):
                    if (
                        previous_current_batch_num != "NS"
                        and previous_current_piece_num != "NS"
                    ):
                        if int(previous_current_batch_num) == int(
                            mod.item(i).text()
                        ) and int(previous_current_piece_num) == int(
                            mod.item(i).child(j).text()
                        ):
                            # Make the old selected black
                            mod.item(i).child(j).setForeground(QColor("black"))
            # Make the item Black in model sorted list
            sortedMod = self.sortedModelList.model()
            for i in range(sortedMod.rowCount()):

                if (
                    previous_current_batch_num != "NS"
                    and previous_current_piece_num != "NS"
                ):

                    if (
                        sortedMod.item(i).text()
                        == f"Batch {int(previous_current_batch_num):03}, model: {int(previous_current_piece_num)}"
                    ):

                        (sortedMod.item(i)).setForeground(QColor("black"))
            # Also we need to unred the previous selected item in the sorted model list

            # Remove the dict entry from
            dict_key = f"{easting},{northing },{context},{int(num)}"
            self._3d_model_dict[dict_key] = (None, None)
            self.current_batch.setText(f"NS")
            self.current_piece.setText(f"NS")

            # Remove the current 3d model


def main():
    """Main function."""
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # Show the calculator's GUI
    main = MainWindow()
    main.show()
    # Execute the calculator's main loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
