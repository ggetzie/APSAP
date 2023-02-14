import ctypes

opengl_path = "./computation/opengl32.dll"
ctypes.cdll.LoadLibrary(opengl_path)

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from view.mixins.ply_window import PlyWindowMixin
from controller.main_controller import MainController


class MainView(QMainWindow, PlyWindowMixin):
    """View (GUI)."""

    def __init__(self):
        """View initializer."""
        super(MainView, self).__init__()

        # model, view, controller

        #Setting up model
     #   self.main_model = main_model
        
        #Load the data needed in the mainmodel
    #    self.main_model.prepare_data(self)


        #Setting up view
        uic.loadUi("view/MainWindow.ui", self)
        self.set_up_ply_window()

        #Setting up controller
        #self.main_controller = MainController(self, self.main_model)
      
        #self.set_up_view_controller_connection()


        # Remove the current 3d model


    def set_up_view_controller_connection(self, main_controller ):

        main_view = self
        main_view.finds_list.currentItemChanged.connect(main_controller.load_find_images)

        main_view.update_button.clicked.connect(main_controller.add_match)
        main_view.remove_button.clicked.connect(main_controller.remove_match)

        #These 
        main_view.hemisphere_cb.currentIndexChanged.connect(main_controller.populate_zones)
        main_view.zone_cb.currentIndexChanged.connect(main_controller.populate_eastings)
        main_view.easting_cb.currentIndexChanged.connect(main_controller.populate_northings)
        main_view.northing_cb.currentIndexChanged.connect(main_controller.populate_contexts)
        main_view.context_cb.currentIndexChanged.connect(main_controller.contextChanged)

