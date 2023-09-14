
from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QPixmap
from random import randint

class ImageWindow(QWidget):
 

    def __init__(self, current_image):
        super().__init__()
        layout = QVBoxLayout()
        main_view = self
        main_view.label = QLabel("iamge_window")
        pixmap = QPixmap(current_image)
        pixmap = pixmap.scaledToWidth(720)
        main_view.label.setPixmap(pixmap)
        layout.addWidget(main_view.label)
        main_view.setLayout(layout)

class OpenImageMixin:
    # What you do when you click on the front and back images

    def set_up_images_pop_up(self):
        main_view = self
        main_view.findFrontPhoto_l.mousePressEvent = main_view.open_image_front
        main_view.findBackPhoto_l.mousePressEvent = main_view.open_image_back

    def open_image_front(self , event):
        main_view = self 
        if main_view.findFrontPhoto_l.pixmap():
            main_view.wid = ImageWindow(main_view.current_image_front)
            main_view.wid.show()
        
    def open_image_back(self , event):
        main_view = self 
        if main_view.findBackPhoto_l.pixmap():
            main_view.wid = ImageWindow(main_view.current_image_back)
            main_view.wid.show()
