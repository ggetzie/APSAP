import ctypes

#opengl_path = r".\computation\opengl32.dll"
#ctypes.cdll.LoadLibrary(opengl_path)
 
from view.mixins.ply_window import PlyWindowMixin
from view.mixins.image_window import OpenImageMixin
from view.mixins.about_window import AboutMixin

from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PyQt5 import  uic
import os
 



class MainView(QMainWindow, PlyWindowMixin, OpenImageMixin, AboutMixin):
    """View (GUI)."""

    def __init__(self):
        """View initializer."""
        super(MainView, self).__init__()
        uic.loadUi("view/ui_files/MainWindow.ui", self)
         
        # self.set_up_weight_adjustment_widget()
        self.set_up_ply_window()
        self.set_up_images_pop_up()
        


    def set_up_view_presenter_connection(self, main_presenter, main_model):

        main_view = self
        main_view.finds_list.currentItemChanged.connect(main_presenter.load_find_images)
        main_view.update_button.clicked.connect(main_presenter.add_match)
        main_view.remove_button.clicked.connect(main_presenter.remove_match)
 
        main_view.hemisphere_cb.currentIndexChanged.connect(
            main_presenter.populate_zones
        )
        main_view.zone_cb.currentIndexChanged.connect(main_presenter.populate_eastings)
        main_view.easting_cb.currentIndexChanged.connect(
            main_presenter.populate_northings
        )
        main_view.northing_cb.currentIndexChanged.connect(
            main_presenter.populate_contexts
        )       
        main_view.context_cb.currentIndexChanged.connect(
          lambda:   self.set_filter (main_model, main_presenter)
        )
        main_view.batch_start.valueChanged.connect(lambda: self.setUpBatchFilter (main_presenter)) 
        main_view.batch_end.valueChanged.connect(lambda: self.setUpBatchFilter (main_presenter)) 
        main_view.find_start.valueChanged.connect(lambda: self.setUpBatchFilter (main_presenter)) 
        main_view.find_end.valueChanged.connect(lambda: self.setUpBatchFilter (main_presenter)) 
        main_view.loadContext.clicked.connect(main_presenter.contextChanged)
        main_view.loadSortedPlys.clicked.connect(lambda: main_presenter.load_sorted_models (main_view.finds_list.currentItem()))


    def checkBatchValid(self):
        main_view = self
        if main_view.batch_start.value() > main_view.batch_end.value():
            return False
        return True

    def setUpBatchFilter(self, main_presenter):
        main_view = self
        if self.checkBatchValid():
            main_view.batch_error.setText("")
            
        else:
            main_view.batch_error.setText("Start must be smaller than End")
        if self.checkFindsValid():
            main_view.find_error.setText("")
            
        else:
            main_view.find_error.setText("Start must be smaller than End")

    def checkFindsValid(self):
        main_view = self
        if main_view.find_start.value() > main_view.find_end.value():
            return False
        return True

    


    def set_filter(self, main_model, main_presenter):
        main_view = self
        #Deselect finds list
        main_view.finds_list.setCurrentItem(None)
        main_view.finds_list.clear()

        # #Remove all 3d models from 
        # main_view.sorted_model_list.clear()

        main_presenter.clearInterface()
        #When we load finds, we also know the years the 3d models belong to 
        from glob import glob
        context_dir = main_presenter.get_context_dir()
        from pathlib import Path
        
        #We first set the min and max of the filter 
        years_folder_path = (context_dir / main_model.path_variables["BATCH_3D_SUBDIR"]/"*").as_posix()
        years = [Path(path).parts[-1] for path in glob(years_folder_path)]
        
        if not years: #Empty
            main_view.year.setMinimum(0)
            main_view.year.setMaximum(0)
            main_view.year.setReadOnly(True)
        else:
            yearsSet = set()
            for year in years:
                try:
                    yearsSet.add(int(year))
                except:
                    pass
            main_view.year.setMinimum(min(yearsSet))
            main_view.year.setMaximum(max(yearsSet))
            main_view.year.setReadOnly(False)

        batch_nums_folder_path = (context_dir / main_model.path_variables["BATCH_3D_SUBDIR"]/"*"/"*").as_posix()
        #One line to turn the get all batch numbers situated in the year(s) folder of a context
        batch_nums = []
        for path in glob(batch_nums_folder_path):
             if "batch_" == Path(path).parts[-1][:6]:
                batch_nums.append(int(Path(path).parts[-1].replace("batch_","")) )
         

        if batch_nums:
            batch_min = min(batch_nums)
            batch_max = max(batch_nums)
            main_view.batch_start.setReadOnly(False)
            main_view.batch_end.setReadOnly(False)

        else:
            batch_min = 0
            batch_max = 0
            main_view.batch_start.setReadOnly(True)
            main_view.batch_end.setReadOnly(True)
        
        main_view.batch_start.setMinimum(batch_min)
        main_view.batch_start.setMaximum(batch_max)
        main_view.batch_start.setValue(batch_min)
        main_view.batch_end.setMinimum(batch_min)
        main_view.batch_end.setMaximum(batch_max)
        main_view.batch_end.setValue(batch_max)

        #Get all find numbers where both 1.jpg and 2.jpg exist
        finds_photo_dir = main_model.path_variables["FINDS_PHOTO_DIR"]
        
        #finds_path = glob(context_dir / main_model.path_variables["FINDS_SUBDIR"]/"*"  / finds_photo_dir / "1.jpg").as_posix() + glob(context_dir / main_model.path_variables["FINDS_SUBDIR"]/"*"  / finds_photo_dir / "2.jpg").as_posix()
        #finds_path_set = set(finds_path)
        nums = glob((context_dir / main_model.path_variables["FINDS_SUBDIR"]/"*" ).as_posix())
        find_nums = []
        for i in nums:
            path1 = Path(i)/finds_photo_dir / "1.jpg"
            path2 = Path(i)/finds_photo_dir / "2.jpg"
            if os.path.exists(path1) and os.path.exists(path2):
                if Path(i).parts[-1].isnumeric():
                    find_nums.append(int(Path(i).parts[-1]))
        

        print(f"find_nums: {find_nums}")
        if find_nums:
            find_min = min(find_nums)
            find_max = max(find_nums)
            main_view.find_start.setReadOnly(False)
            main_view.find_end.setReadOnly(False)
        else:
            find_min = 0
            find_max = 0
            main_view.find_start.setReadOnly(True)
            main_view.find_end.setReadOnly(True)

        
        main_view.find_start.setMinimum(find_min)
        main_view.find_start.setMaximum(find_max)
        main_view.find_start.setValue(find_min)
        main_view.find_end.setMinimum(find_min)
        main_view.find_end.setMaximum(find_max)
        main_view.find_end.setValue(find_max)
        #Do the same thing except this time, we set the min and max if finds

