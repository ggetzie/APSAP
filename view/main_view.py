import ctypes

#opengl_path = r".\computation\opengl32.dll"
#ctypes.cdll.LoadLibrary(opengl_path)
 
from view.mixins.ply_window import PlyWindowMixin
from view.mixins.image_window import OpenImageMixin
from view.mixins.adjust_window import AdjustWindowMixin, AdjustWindow
from view.mixins.about_window import AboutMixin

from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PyQt5 import  uic

 



class MainView(QMainWindow, PlyWindowMixin, OpenImageMixin, AdjustWindowMixin, AboutMixin):
    """View (GUI)."""

    def __init__(self):
        """View initializer."""
        super(MainView, self).__init__()
        uic.loadUi("view/ui_files/MainWindow.ui", self)
        self.set_up_weight_adjustment_widget()
        self.set_up_ply_window()
        self.set_up_images_pop_up()
        self.menubar.setVisible(False)
 


    def set_up_view_presenter_connection(self, main_presenter):

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
       # main_view.context_cb.currentIndexChanged.connect(main_presenter.contextChanged)
        main_view.actionWeights_Adjustments.triggered.connect(self.show_popup)
        main_view.actionAbout.triggered.connect(self.showAbout)
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
        

