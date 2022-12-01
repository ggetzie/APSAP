import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtGui import QColor, QIcon, QPixmap, QImage, QWindow, QStandardItem, QStandardItemModel, QMovie, QPainter
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QListWidgetItem, QFileDialog, QMessageBox, QSplashScreen
import os
import pathlib
import open3d as o3d
import re
from database_tools import get_pottery_sherd_info, update_match_info
from glob import glob as glob
import win32gui
import json
import numpy as np
basedir = pathlib.Path().resolve() 
from area_detect import AreaComparator
from components.vis import Visualized
from components.pop_up import PopUp
from ColorSummary import get_image_summary_from_2d, get_image_summary_from_3d

#sample_3d_image
# FILE_ROOT = pathlib.Path("D:\\ararat\\data\\files")
FINDS_SUBDIR = "finds/individual"
BATCH_3D_SUBDIR = "finds/3dbatch"
FINDS_PHOTO_DIR = "photos"
MODELS_FILES_DIR = "finds/3dbatch/2022/batch_*/registration_reso1_maskthres242/final_output/piece_*_world.ply"
MODELS_FILES_RE = "finds/3dbatch/2022/batch_(.+?)/registration_reso1_maskthres242/final_output/piece_(.+?)_world.ply"
HEMISPHERES = ("N", "S")

 

class MainWindow(QMainWindow, PopUp, Visualized):
    """View (GUI)."""


    def __init__(self):
        """View initializer."""
        super(MainWindow, self).__init__()

        uic.loadUi("qtcreator/MainWindow.ui", self)
        if not self.check_has_path_in_setting():        
            self.ask_for_prompt()
        
        setting = json.load(open("settings.json"))
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

    def check_has_path_in_setting(self):
        setting_found = pathlib.Path("./settings.json").is_file()  
        if not setting_found:
            return False
        else:
            setting_dict = json.load(open("settings.json")) if setting_found else {}  
            key_exist = "FILE_ROOT" in setting_dict
            if key_exist:
                path_exist =  pathlib.Path(setting_dict["FILE_ROOT"]).is_dir()
                if path_exist: #Only case when we don't have to ask for a path
                    return True
                else:
                    return False
            else:
                return False

    def update_button_click(self, e):
        if e.text() == "OK":
            easting, northing, context =  (self.get_easting_northing_context())
            find_num = self.selected_find.text()
            batch_num = self.new_batch.text()
            piece_num = self.new_piece.text()
            if easting and northing and context and find_num and batch_num and piece_num:
                update_match_info(easting, northing,context, int(find_num),int(batch_num),int(piece_num))
                #Here to avoid loading time, we manually update some data. We can
                #reload the contexts but it would be way too slow
                batch_num = self.new_batch.text()
                piece_num = self.new_piece.text()
                if hasattr(self,  "selected_find_widget"):
                    self.selected_find_widget.setForeground(QColor("red"))
                self.current_batch.setText(batch_num)
                self.current_piece.setText(piece_num)
                #Here's let's try to get color red
 
                mod = self.modelList.model()
                #Make the item red in modelList
                for i in range(mod.rowCount()):

                    for j in range(mod.item(i).rowCount()):
                        if int(batch_num) == int(mod.item(i).text()) and int(piece_num) == int(mod.item(i).child(j).text()):
                            mod.item(i).child(j).setForeground(QColor("red"))
                #Make the item red in sortedModelList
                sortedMod = self.sortedModelList.model()
                for i in range(sortedMod.rowCount()):
                    #f"{int(_3d_locations[0]):03}", 1).replace("*", f"{int(_3d_locations[1])}
                    if sortedMod.item(i).text() == f"Batch {int(batch_num):03}, model: {int(piece_num)}":
                        (sortedMod.item(i)).setForeground(QColor("red"))
            else:
                QMessageBox(self,text="Please select both a find and a model").exec()
    def update_model_db(self):
 
            find_num = self.selected_find.text()
            batch_num = self.new_batch.text()
            piece_num = self.new_piece.text()
            msg = QMessageBox()
            msg.setText(f"Find ({find_num}) will be updated to 3d Batch ({batch_num}) 3d Piece ({piece_num}). Proceed?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.buttonClicked.connect(self.update_button_click)
            msg.exec()
            
        #Remember to refresh
    

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
        
        funcs_to_run = [["Loading finds. It might take a while", self.populate_finds],["Loading models. It might take a while",self.populate_models]]
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

    def populate_models(self):
 
        path =  (str((self.get_context_dir()/MODELS_FILES_DIR)))
        all_model_paths = (glob(path))
        if not all_model_paths:
            self.statusLabel.setText(f"No models were found")
        #Setting up the model
        model = QStandardItemModel(self)
        model.setHorizontalHeaderLabels(["Models"])
        #Getting a dict for all the batches
        batches_dict = dict()
        for  path in (all_model_paths):
            m = re.search( MODELS_FILES_RE, path.replace("\\", "/"))
            #This error happens when the relative path is different
            batch_num = m.group(1)
            piece_num = m.group(2)
            if batch_num not in batches_dict:
                batches_dict[batch_num] = [[int(piece_num), path]]
            else:
                batches_dict[batch_num].append([int(piece_num), path])
        #Sort the items
        for key in batches_dict:
            batches_dict[key] = sorted(batches_dict[key])
            
        all_matched_3d_models = set()
 
        for key in (self._3d_model_dict):
            if not (self._3d_model_dict[key][0] == None and self._3d_model_dict[key][1] == None):
                all_matched_3d_models.add(self._3d_model_dict[key])
 
        print(all_matched_3d_models)
        #Add all items onto the QTree
        actual_index = 0
        self.get_2d_areas()
        all_3d_areas  = []
        all_3d_color_summaries = []
        for batch in batches_dict:
            items =  batches_dict[batch]
            batch = QStandardItem(f"{batch}")
            all_3d_area = []
            all_3d_color_summary = []
            for item in  items:
                index = item[0]
                path = item[1]
                m = re.search( MODELS_FILES_RE, path.replace("\\", "/"))
                #This error happens when the relative path is different
                batch_num = m.group(1)
                piece_num = m.group(2)
 

                area = self.area_comparator.get_3d_object_area(path)
                color_summary = (get_image_summary_from_3d(path,self.vis))
                print(f"index: {actual_index}: 3dArea: {area}")
                all_3d_area.append([area, batch_num,piece_num ])
                all_3d_color_summary.append([color_summary, batch_num,piece_num ])
                ply = QStandardItem(f"{index}")
                ply.setData(f"{path}", Qt.UserRole) 
                if (int(batch_num), int(piece_num)) in all_matched_3d_models:
                    ply.setForeground(QColor("red"))
                batch.appendRow(ply)
                actual_index += 1
            all_3d_areas.append(all_3d_area)
            all_3d_color_summaries.append(all_3d_color_summary)
            model.appendRow(batch)
        self.all_3d_areas = (all_3d_areas)
        self.all_3d_color_summaries = all_3d_color_summaries
        self.modelList.setModel(model)
        self.modelList.selectionModel().currentChanged.connect(self.change_3d_model)
    
    def get_easting_northing_context(self):
        context_dir = self.get_context_dir()
        path_parts = (pathlib.Path(context_dir).parts[-3:])
        easting =  int(path_parts[0])
        northing = int(path_parts[1])
        context = int(path_parts[2])
        return (easting, northing, context)
    def get_similaritiy_scores(self, index):
        _2d_area = self.all_2d_areas[int(index) - 1]
        similarity_scores = []
        for i in range(len(self.all_3d_areas)):
            for j in range(len(self.all_3d_areas[i])):
                _3d_area = self.all_3d_areas[i][j][0]
                batch_num = self.all_3d_areas[i][j][1]
                piece_num = self.all_3d_areas[i][j][2]
                similarity_scores.append([max(_3d_area/_2d_area, _2d_area/_3d_area), batch_num, piece_num])
        return similarity_scores
 
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

        funcs_to_run = [["Loading finds. It might take a while", self.populate_finds],["Loading models. It might take a while",self.populate_models]]
        self.load_and_run(funcs_to_run)
    def get_2d_areas(self):
        all_2d_areas = []
        for i in range(self.findsList.count() ):
            
            index = int(self.findsList.item(i).text())
            dir = self.get_context_dir() / FINDS_SUBDIR / str(index) / FINDS_PHOTO_DIR/ "2.jpg"
            area = self.area_comparator.get_2d_picture_area(dir)
            print(f"index: {index}: 2dArea: {area}")
            all_2d_areas.append(area)
        self.all_2d_areas = all_2d_areas
    def populate_finds(self):
        #if self.splash:
        #    self.splash.showMessage("Loading finds")
        self.findsList.clear()
        context_dir = self.get_context_dir()
        finds_dir = context_dir / FINDS_SUBDIR
        finds = [d.name for d in finds_dir.iterdir() if d.name.isdigit()]
        #Getting easting, northing and context for getting doing the query
        easting_northing_context = self.get_easting_northing_context()
        finds.sort(key=lambda f: int(f))
        
        #Get a dictionary to get all 
        self._3d_model_dict = dict()
        for find in finds:
            item = QListWidgetItem(find)
            _3d_locations = get_pottery_sherd_info(easting_northing_context[0], easting_northing_context[1], easting_northing_context[2], int(find))
         
            
            if _3d_locations[0] != None and _3d_locations[1] != None:
                item.setForeground(QColor("red"))
            self.findsList.addItem(item)
            self._3d_model_dict[f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find)}"] = _3d_locations


              
    def load_find_images(self, selected_item):
        self.selected_find_widget = selected_item
        try:
            find_num = self.findsList.currentItem().text()
        except AttributeError:
            self.findFrontPhoto_l.clear()
            self.findBackPhoto_l.clear()
            return
        

        photos_dir = self.get_context_dir() / FINDS_SUBDIR / find_num / FINDS_PHOTO_DIR
 
        front_photo = QImage(str(photos_dir / "1.jpg"))
        back_photo = QImage(str(photos_dir / "2.jpg"))

        self.findFrontPhoto_l.setPixmap(
            QPixmap.fromImage(front_photo).scaledToWidth(self.findFrontPhoto_l.width())
        )
        self.findBackPhoto_l.setPixmap(
            QPixmap.fromImage(back_photo).scaledToWidth(self.findBackPhoto_l.width())
        )
        self.selected_find.setText(find_num)
        easting_northing_context = self.get_easting_northing_context()
        _3d_locations = get_pottery_sherd_info(easting_northing_context[0], easting_northing_context[1], easting_northing_context[2], int(find_num))
        if _3d_locations[0] != None and _3d_locations[1] != None:
            self.current_batch.setText(str(_3d_locations[0]))
            self.current_piece.setText(str(_3d_locations[1]))
            #Change to the piece matched as default
          
            path =  (str((self.get_context_dir()/MODELS_FILES_DIR)))
            whole_path = (path.replace("*", f"{int(_3d_locations[0]):03}", 1).replace("*", f"{int(_3d_locations[1])}", 1)) 
            current_pcd_load = o3d.io.read_point_cloud(whole_path)
            if hasattr(self, "current_pcd") :
                self.change_model(current_pcd_load, self.current_pcd)
            else:
                self.change_model(current_pcd_load, None)
                
        else:
            self.current_batch.setText("NS")
            self.current_piece.setText("NS")
            
        #We have an image chosen, we can get the simlarity scores against all 3d model's images
        flat_simllarity_list  = self.get_similaritiy_scores(find_num)
 
        all_matched_3d_models = set()
        
        for key in (self._3d_model_dict):
            if not (self._3d_model_dict[key][0] == None and self._3d_model_dict[key][1] == None):
                all_matched_3d_models.add(self._3d_model_dict[key])
     
    
        #python sort by first element of list by default
     
        model = QStandardItemModel(self)
        model.setHorizontalHeaderLabels(["Sorted models"])
        
        for score_i_j_tuple in sorted(flat_simllarity_list):
            ply = QStandardItem(f"Batch {score_i_j_tuple[1]}, model: {score_i_j_tuple[2]}")
            path =  (str((self.get_context_dir()/MODELS_FILES_DIR)))
            whole_path = (path.replace("*", f"{int(score_i_j_tuple[1]):03}", 1).replace("*", f"{int(score_i_j_tuple[2])}", 1)) 
            if (int(score_i_j_tuple[1]), int(score_i_j_tuple[2])) in all_matched_3d_models:
                    ply.setForeground(QColor("red"))
            ply.setData(f"{whole_path}", Qt.UserRole) 
            
            model.appendRow(ply)
        self.sortedModelList.setModel(model)
        self.sortedModelList.selectionModel().currentChanged.connect(self.change_3d_model)
    
 
       
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