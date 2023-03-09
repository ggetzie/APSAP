import ctypes

opengl_path = "./computation/opengl32.dll"
ctypes.cdll.LoadLibrary(opengl_path)

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from view.mixins.ply_window import PlyWindowMixin
from presenter.main_presenter import Mainpresenter
from PIL import Image
from random import randint

from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QPixmap

class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent,
    it will appear as a free-floating window.
    """

    def __init__(self, current_image_front):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window % d" % randint(0, 100))
        pixmap = QPixmap(current_image_front)
        self.label.setPixmap(pixmap)
        layout.addWidget(self.label)
        self.setLayout(layout)

class MainView(QMainWindow, PlyWindowMixin):
    """View (GUI)."""

    def __init__(self):
        """View initializer."""
        super(MainView, self).__init__()
        uic.loadUi("view/MainWindow.ui", self)
        self.initialize_feature_weights()
        self.set_up_ply_window()
        self.get_features_weights()
        self.wid = None
        self.findFrontPhoto_l.mousePressEvent = self.open_image
        self.findBackPhoto_l.mousePressEvent = self.open_image_back



    def open_image(self , event):
   
        if self.findFrontPhoto_l.pixmap():
            self.wid = AnotherWindow(self.current_image_front)
            self.wid.show()
    def open_image_back(self , event):
   
        if self.findBackPhoto_l.pixmap():
            self.wid = AnotherWindow(self.current_image_back)
            self.wid.show()
    def start_window(self):
        pass
    def set_up_view_presenter_connection(self, main_presenter):

        main_view = self
        main_view.finds_list.currentItemChanged.connect(main_presenter.load_find_images)
        main_view.update_button.clicked.connect(main_presenter.add_match)
        main_view.remove_button.clicked.connect(main_presenter.remove_match)
        main_view.update_weights_button.clicked.connect(main_view.get_features_weights)

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
        main_view.context_cb.currentIndexChanged.connect(main_presenter.contextChanged)
    
    def initialize_feature_weights(self):
        main_view = self

        initial_weights = {'area_similarity': 1.0, 'brightness_similarity': 0.84, 'brightness_std_similarity': 0.21, 'width_length_similarity': 0.46,   'extra_similarities': 0.08}
        main_view.areaSlider.setValue(initial_weights["area_similarity"]*100)
        main_view.brightnessSlider.setValue(initial_weights["brightness_similarity"]*100)
        main_view.brightnessStdSlider.setValue(initial_weights["brightness_std_similarity"]*100)
        main_view.widthLengthSlider.setValue(initial_weights["width_length_similarity"]*100)
        main_view.identifierSlider.setValue(initial_weights["extra_similarities"]*100)
    def get_features_weights(self):
        main_view = self
 
        weights = {
                "area_similarity": int(main_view.areaSlider.value())/100 ,
                "brightness_similarity": int(main_view.brightnessSlider.value())/100,
                "brightness_std_similarity": int(main_view.brightnessStdSlider.value())/100,
                "width_length_similarity" : int(main_view.widthLengthSlider.value())/100,
                
                "extra_similarities": int(main_view.identifierSlider.value())/100
        }
        main_view.weights = weights
        print(weights)