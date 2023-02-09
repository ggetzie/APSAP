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
        self.mainModel = mainModel
        uic.loadUi("view/MainWindow.ui", self)
        self.mainController = MainController(self, self.mainModel)
        self.set_up_3d_window()

        self.findsList.currentItemChanged.connect(self.load_find_images)

        self.update_button.clicked.connect(self.mainController.update_model_db)
        self.remove_button.clicked.connect(self.mainController.remove_match)

        # Remove the current 3d model
