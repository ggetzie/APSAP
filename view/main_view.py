# import ctypes
import logging
import pathlib
import subprocess
import time

# opengl_path = r".\computation\opengl32.dll"
# ctypes.cdll.LoadLibrary(opengl_path)

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PIL import Image
from PIL.ImageQt import ImageQt

from view.mixins.ply_window import PlyWindowMixin
from view.mixins.image_window import OpenImageMixin

logger = logging.getLogger(__name__)


class MainView(QMainWindow, PlyWindowMixin, OpenImageMixin):
    """The MainView contains all the GUI related functions and classes

    Args:
        QMainWindow (QMainWindow): Making the MainView a QWidget that can load a
        ui file and display things.

        PlyWindowMixin (class): Mixin that initializes the window that displays 3d models in it.

        OpenImageMixin (class): Mixin that allows the users to click on an
        Image to see it full size.
    """

    def __init__(self):
        """This constructor loads the ply to the ui file, set up the 3d model window,
        and make it the images pop when you click on them.
        """
        super().__init__()
        logger.info("Loading MainWindow.ui")
        now = time.time()
        uic.loadUi("view/ui_files/MainWindow.ui", self)
        logger.info("MainWindow.ui loaded in %s seconds", (f"{time.time() - now:0.4f}"))
        now = time.time()
        logger.info("Setting up ply window")
        self.set_up_ply_window()
        logger.info("Ply window set up in %s seconds", (f"{time.time() - now:0.4f}"))
        logger.info("Setting up images pop up")
        now = time.time()
        self.set_up_images_pop_up()
        logger.info("Images pop up set up in %s seconds", (f"{time.time() - now:0.4f}"))
        self.current_image_front = ""
        self.current_image_back = ""

        ## append the version to the window title
        version = self.get_version()
        self.setWindowTitle(f"Sherd Match Assistance Version: {version}")

    def get_version(self):
        try:
            cwd = pathlib.Path(__file__).parent
            result = subprocess.run(
                ["git", "describe", "--tags", "--always", "--dirty"],
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd,
            )
            logger.info("Version: %s", result.stdout.strip())
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error("Error getting version: %s", e.stderr)
            return "Unknown"

    def display_error(self, message: str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def display_find_photo(self, side: str, photo_path: pathlib.Path):
        """This function displays the photo of the selected find on the GUI

        Args:
            side (str): The side of the photo to display. Must be "front" or "back"
        """
        try:
            photo = (
                Image.open(photo_path).resize((450, 300), Image.LANCZOS).convert("RGB")
            )
        except (FileNotFoundError, IOError, OSError, TypeError, ValueError) as e:
            logger.error("Error opening photo at %s: %s", photo_path, e)
            self.clear_find_photos()
            self.display_error(f"Error opening photo: {e}")
            return

        im_qt = ImageQt(photo)
        pix_map = QPixmap.fromImage(im_qt)
        if side == "front":
            self.findFrontPhoto_l.setPixmap(
                pix_map.scaledToWidth(self.findFrontPhoto_l.width())
            )
            self.current_image_front = str(photo_path)
        else:
            self.findBackPhoto_l.setPixmap(
                pix_map.scaledToWidth(self.findBackPhoto_l.width())
            )
            self.current_image_back = str(photo_path)

    def clear_find_photos(self):
        self.findFrontPhoto_l.clear()
        self.findBackPhoto_l.clear()
        self.current_image_front = ""
        self.current_image_back = ""
