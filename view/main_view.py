import ctypes

opengl_path = "./computation/opengl32.dll"
ctypes.cdll.LoadLibrary(opengl_path)
import sys
from PyQt5 import uic, QtGui, QtCore
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from view.mixins.ply_window import PlyWindowMixin
from presenter.main_presenter import Mainpresenter
from PIL import Image
from random import randint
from PyQt5.QtWidgets import QMessageBox
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets, uic


class Adjust(QtWidgets.QWidget):
    def __init__(self):
        super(Adjust, self).__init__()
        uic.loadUi("view/adjust.ui", self)


class AdjustAnotherWindow(QWidget):
 
    def __init__(self, sliders):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("something something")
        adj = Adjust()
  
        sliders["areaSlider"] = adj.areaSlider
        sliders["brightnessSlider"] = adj.brightnessSlider
        sliders["brightnessStdSlider"] = adj.brightness_std_similarity
        sliders["widthLengthSlider"] = adj.width_length_similarity
        sliders["identifierSlider"] = adj.extra_similarities
         

        layout.addWidget( adj)
        
        self.setLayout(layout)


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
        self.sliders = {}
        self.sliders_window = AdjustAnotherWindow(self.sliders) 

        self.initialize_feature_weights()
        self.set_up_ply_window()
        self.get_features_weights()
        self.wid = None
        self.findFrontPhoto_l.mousePressEvent = self.open_image
        self.findBackPhoto_l.mousePressEvent = self.open_image_back
        
    def slidersChangedReactions(self):
        pass

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
        main_view.actionWeights_Adjustments.triggered.connect(self.show_popup)
    def initialize_feature_weights(self):
        main_view = self

        initial_weights = {'area_similarity': 1.0, 'brightness_similarity': 0.84, 'brightness_std_similarity': 0.21, 'width_length_similarity': 0.46,   'extra_similarities': 0.08}
        
        main_view.sliders["areaSlider"].setValue(initial_weights["area_similarity"]*100)
        main_view.sliders["brightnessSlider"].setValue(initial_weights["brightness_similarity"]*100)
        main_view.sliders["brightnessStdSlider"].setValue(initial_weights["brightness_std_similarity"]*100)
        main_view.sliders["widthLengthSlider"].setValue(initial_weights["width_length_similarity"]*100)
        main_view.sliders["identifierSlider"].setValue(initial_weights["extra_similarities"]*100)
    def get_features_weights(self):
        main_view = self
 
        weights = {
                "area_similarity": int(main_view.sliders["areaSlider"].value())/100 ,
                "brightness_similarity": int(main_view.sliders["brightnessSlider"].value())/100,
                "brightness_std_similarity": int(main_view.sliders["brightnessStdSlider"].value())/100,
                "width_length_similarity" : int(main_view.sliders["widthLengthSlider"].value())/100,
                
                "extra_similarities":  int(main_view.sliders["identifierSlider"].value())/100
        }
        return weights
         
      
    def show_popup(self):
        self.sliders_window.show()
 