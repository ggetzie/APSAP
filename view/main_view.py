import ctypes

import logging
import pathlib
import subprocess

# opengl_path = r".\computation\opengl32.dll"
# ctypes.cdll.LoadLibrary(opengl_path)
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic

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
        uic.loadUi("view/ui_files/MainWindow.ui", self)

        self.set_up_ply_window()
        self.set_up_images_pop_up()
        self.threadpool = QThreadPool()
        version = self.get_version()
        ## append the version to the window title
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

