import sys

opengl_path = "./computation/opengl32.dll"
import ctypes

ctypes.cdll.LoadLibrary(opengl_path)
from PyQt5 import uic
from PyQt5.QtGui import (
    QColor,
)
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
)

from model.database.database_tools import  update_match_info
from view.vis import Visualized
from view.pop_up import PopUp
from view.load_qt_images_models import LoadImagesModels

from controller.mainController import MainController
from model.mainModel import MainModel

# Here let's do some simple machine learning to get


class MainView(QMainWindow, PopUp, Visualized, LoadImagesModels):
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

        self.update_button.clicked.connect(self.update_model_db)
        self.remove_button.clicked.connect(self.remove_match)




    def remove_match(self):
        # This functions removes the match between the image and the 3d model
        selected_item = self.findsList.currentItem()

        # Only remove model when an image is selected
        if selected_item:
            num = selected_item.text()
            selected_item.setForeground(QColor("black"))
            # Update the database
            (
                easting,
                northing,
                context,
            ) = self.mainController.get_easting_northing_context()
            update_match_info(easting, northing, context, num, None, None)
            # Unred the matched items in the 3d models list
            previous_current_batch_num = self.current_batch.text()
            previous_current_piece_num = self.current_piece.text()

            mod = self.modelList.model()
            # Make the item Black in modelList
            for i in range(mod.rowCount()):
                for j in range(mod.item(i).rowCount()):
                    if (
                        previous_current_batch_num != "NS"
                        and previous_current_piece_num != "NS"
                    ):
                        if int(previous_current_batch_num) == int(
                            mod.item(i).text()
                        ) and int(previous_current_piece_num) == int(
                            mod.item(i).child(j).text()
                        ):
                            # Make the old selected black
                            mod.item(i).child(j).setForeground(QColor("black"))
            # Make the item Black in model sorted list
            sortedMod = self.sortedModelList.model()
            for i in range(sortedMod.rowCount()):

                if (
                    previous_current_batch_num != "NS"
                    and previous_current_piece_num != "NS"
                ):

                    if (
                        sortedMod.item(i).text()
                        == f"Batch {int(previous_current_batch_num):03}, model: {int(previous_current_piece_num)}"
                    ):

                        (sortedMod.item(i)).setForeground(QColor("black"))
            # Also we need to unred the previous selected item in the sorted model list

            # Remove the dict entry from
            dict_key = f"{easting},{northing },{context},{int(num)}"
            self._3d_model_dict[dict_key] = (None, None)
            self.current_batch.setText(f"NS")
            self.current_piece.setText(f"NS")

            # Remove the current 3d model