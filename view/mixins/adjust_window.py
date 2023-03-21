from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow
 
from presenter.main_presenter import Mainpresenter
 
from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PyQt5 import QtWidgets 

class Adjust(QtWidgets.QWidget):
    def __init__(self):
        super(Adjust, self).__init__()
        uic.loadUi("view/ui_files/adjust.ui", self)


class AdjustWindow(QWidget):
 
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

class AdjustWindowMixin:

    def set_up_weight_adjustment_widget(self):
        self.sliders = {}
        self.sliders_window = AdjustWindow(self.sliders) 
        self.initialize_feature_weights()
        self.get_features_weights()
        
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
 