# import ctypes
import logging
import pathlib
import subprocess
import time

# opengl_path = r".\computation\opengl32.dll"
# ctypes.cdll.LoadLibrary(opengl_path)

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QListWidget, QTreeView
from PyQt5.QtGui import QPixmap, QColor, QStandardItemModel
from PyQt5 import uic, QtCore
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
        self.finds_list: QListWidget = None
        self.modelList: QTreeView = None
        self.sorted_model_list: QTreeView = None
        self.current_pcd = None
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

    def clear_find_info(self):
        self.clear_find_photos()
        self.selected_find_info.setText("")
        self.selected_find.setText("")
        self.current_batch.setText("")
        self.current_year.setText("")
        self.current_piece.setText("")

    def confirm(self, message: str, on_confirm):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Confirm")
        msg.setInformativeText(message)
        msg.setWindowTitle("Confirm")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.buttonClicked.connect(on_confirm)
        msg.exec_()

    def set_find_color(self, find_number: int, color: str):
        find_item = self.finds_list.findItems(str(find_number), QtCore.Qt.MatchExactly)[
            0
        ]
        find_item.setForeground(QColor(color))

    def set_unsorted_model_color(
        self, batch_year: int, batch_number: int, batch_piece: int, color: str
    ):
        # set the piece number to color in the tree view under batch_year -> batch_number
        q_model = self.modelList.model()
        for i in range(q_model.rowCount()):
            for j in range(q_model.item(i).rowCount()):
                for k in range(q_model.item(i).child(j).rowCount()):
                    if (
                        int(q_model.item(i).text()) == batch_year
                        and int(q_model.item(i).child(j).text()) == batch_number
                        and int(q_model.item(i).child(j).child(k).text()) == batch_piece
                    ):
                        q_model.item(i).child(j).child(k).setForeground(QColor(color))

    def set_sorted_model_color(self, model_str: str, color: str):
        # set the piece number to color in the tree view under batch_year -> batch_number
        q_model = self.sorted_model_list.model()
        for i in range(q_model.rowCount()):
            if q_model.item(i).text() == model_str:
                q_model.item(i).setForeground(QColor(color))

    def clear_interface(self):
        """Clear all the texts, and selects, images displayed and 3d models from the interface."""

        self.findFrontPhoto_l.clear()
        self.findBackPhoto_l.clear()
        self.statusLabel.setText("")
        self.selected_find.setText("")
        self.current_batch.setText("")
        self.current_year.setText("")
        self.current_piece.setText("")
        self.new_batch.setText("")
        self.new_piece.setText("")
        self.new_year.setText("")
        self.contextDisplay.setText("")
        if hasattr(self, "current_pcd"):
            self.ply_window.remove_geometry(getattr(self, "current_pcd"))
            setattr(self, "current_pcd", None)

        model = QStandardItemModel(self)
        self.sorted_model_list.setModel(model)
        self.clear_unsorted_models()
        # self.reset_ply_selection_model()
        self.finds_list.setCurrentItem(None)
        self.finds_list.clear()

    def initialize_unsorted_models(self):
        model = QStandardItemModel(self)
        model.setHorizontalHeaderLabels(["Models"])
        self.modelList.setModel(model)

    def clear_unsorted_models(self):
        """This function ensures that there is a empty modelList
        in the view
        """

        self.modelList.selectionModel().model().removeRows(
            0, self.modelList.selectionModel().model().rowCount()
        )

    def clear_finds_list(self):
        self.finds_list.clear()
