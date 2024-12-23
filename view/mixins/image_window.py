import logging
from pathlib import Path
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap

logger = logging.getLogger(__name__)


class ImageWindow(QWidget):
    """This QWidget is shown when a person click on findFrontPhoto_l or findBackPhoto_l"""

    def __init__(self, current_image_path: str):
        super().__init__()
        current = Path(current_image_path)
        self.setWindowTitle(f"Image: {current.stem}")
        larger = current.parent / f"{current.stem}-1500{current.suffix}"
        self.image_path = larger if larger.exists() else current
        self.label = QLabel(f"{current_image_path}")
        logger.debug("current_image_path: %s", current_image_path)
        try:
            photo: Image.Image = Image.open(str(self.image_path))
        except (FileNotFoundError, IOError, OSError, TypeError, ValueError) as e:
            logger.error("Error opening photo at %s: %s", self.image_path, e)
            return
        logger.debug("loaded photo from : %s", self.image_path)
        # 1. Loading from the image path to the pixmap, then to the label.
        im_qt = ImageQt(photo)
        pixmap = QPixmap.fromImage(im_qt)
        logger.debug("photo width: %s", photo.width)
        self.label.setPixmap(pixmap.scaledToWidth(720))

        # 2. Loading from the image label to the layout.
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)


class OpenImageMixin:
    def set_up_images_pop_up(self):
        """This function makes the two image sections of the PYQT web interface clickable,
        when clicked, the image will pop out in a larger window.
        """
        main_view = self
        main_view.findFrontPhoto_l.mousePressEvent = main_view.open_image_front
        main_view.findBackPhoto_l.mousePressEvent = main_view.open_image_back

    def open_image_front(self, event):
        """This function is a callback when the front image is being clicked,
        the image will pop out in a larger window

        Args:
            event (signal): A signal that the front image is clicked
        """
        main_view = self
        if main_view.findFrontPhoto_l.pixmap():
            main_view.wid = ImageWindow(main_view.current_image_front)
            main_view.wid.show()

    def open_image_back(self, event):
        """This function is a callback when the back image is being clicked,
        the image will pop out in a larger window

        Args:
            event (signal): A signal that the back image is clicked
        """
        main_view = self
        if main_view.findBackPhoto_l.pixmap():
            main_view.wid = ImageWindow(main_view.current_image_back)
            main_view.wid.show()
