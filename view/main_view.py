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
        main_view.loadAll.clicked.connect(main_presenter.contextChanged)


    def checkValid(self):
        main_view = self
        if main_view.batch_start.value() > main_view.batch_end.value():
            return False
        return True

    def setUpBatchFilter(self, main_presenter):
        main_view = self
        if self.checkValid():
            main_view.error_message.setText("")
            
        else:
            main_view.error_message.setText("Start should be smaller than End")
        if  main_view.finds_list.currentItem():
                main_presenter.load_find_images(main_view.finds_list.currentItem())   
        
    def set_filter(self, main_model, main_presenter):
        main_view = self
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
                print(path)
                batch_nums.append(int(Path(path).parts[-1].replace("batch_","")) )
         

        if batch_nums:
            batch_min = min(batch_nums)
            batch_max = max(batch_nums)
            main_view.year.setReadOnly(False)
        else:
            batch_min = 0
            batch_max = 0
            main_view.year.setReadOnly(True)
            
        main_view.batch_start.setMinimum(batch_min)
        main_view.batch_start.setMaximum(batch_max)
        main_view.batch_start.setValue(batch_min)
        main_view.batch_end.setMinimum(batch_min)
        main_view.batch_end.setMaximum(batch_max)
        main_view.batch_end.setValue(batch_max)
