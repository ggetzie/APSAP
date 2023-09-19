from PyQt5.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QPixmap


class ImageWindow(QWidget):
    """This QWidget is shown when a person click on findFrontPhoto_l or findBackPhoto_l"""

    def __init__(self, current_image_path):
        super().__init__()

        current_view = self
        current_view.label = QLabel(f"{current_image_path}")

        # 1. Loading from the image path to the pixmap, then to the label.
        pixmap = QPixmap(current_image_path)
        pixmap = pixmap.scaledToWidth(720)
        current_view.label.setPixmap(pixmap)
        
        # 2. Loading from the image laybel to the layout.
        layout = QVBoxLayout()
        layout.addWidget(current_view.label)
        current_view.setLayout(layout)


class OpenImageMixin:
    def set_up_images_pop_up(self):
        """This function makes the two image sections of the PYQT web interface clickable,
        when clicked, the image will pop out in a larger window.
        """
        main_view = self
        main_view.findFrontPhoto_l.mousePressEvent = main_view.open_image_front
        main_view.findBackPhoto_l.mousePressEvent = main_view.open_image_back

    def open_image_front(self, event):
        """This function is a callback when the front image is being clicked, the image will pop out in a larger window

        Args:
            event (signal): A signal that the front image is clicked
        """
        main_view = self
        if main_view.findFrontPhoto_l.pixmap():
            main_view.wid = ImageWindow(main_view.current_image_front)
            main_view.wid.show()

    def open_image_back(self, event):
        """This function is a callback when the back image is being clicked, the image will pop out in a larger window

        Args:
            event (signal): A signal that the back image is clicked
        """
        main_view = self
        if main_view.findBackPhoto_l.pixmap():
            main_view.wid = ImageWindow(main_view.current_image_back)
            main_view.wid.show()
