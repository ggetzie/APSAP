import ctypes

opengl_path = "./computation/opengl32.dll"
ctypes.cdll.LoadLibrary(opengl_path)

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from view.vis import Visualized
 
from view.load_qt_images_models import LoadImagesModels
from controller.mainController import MainController


class MainView(QMainWindow, Visualized, LoadImagesModels):
    """View (GUI)."""

    def __init__(self, mainModel):
        """View initializer."""
        super(MainView, self).__init__()

        # model, view, controller

        #Setting up model
        self.mainModel = mainModel
        
        #Setting up view
        uic.loadUi("view/MainWindow.ui", self)
        self.set_up_3d_window()

        #Setting up controller
        self.mainController = MainController(self, self.mainModel)
      
        self.setUpViewControllerConnection()


        # Remove the current 3d model


    def setUpViewControllerConnection(self):

        view = self
        controller = self.mainController
        view.findsList.currentItemChanged.connect(controller.load_find_images)
        view.sortedModelList.selectionModel().currentChanged.connect(controller.change_3d_model)

        view.update_button.clicked.connect(controller.add_match)
        view.remove_button.clicked.connect(controller.remove_match)

        #These 
        view.hemisphere_cb.currentIndexChanged.connect(controller.populate_zones)
        view.zone_cb.currentIndexChanged.connect(controller.populate_eastings)
        view.easting_cb.currentIndexChanged.connect(controller.populate_northings)
        view.northing_cb.currentIndexChanged.connect(controller.populate_contexts)
        view.context_cb.currentIndexChanged.connect(controller.contextChanged)

