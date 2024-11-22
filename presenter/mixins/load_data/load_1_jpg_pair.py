import logging
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QColor, QStandardItem, QStandardItemModel

# from PyQt5.QtGui import QColor, QPixmap, QStandardItem, QStandardItemModel

# from PyQt5.QtWidgets import QMessageBox

from model.models import year_batch_piece_str

# from PIL.ImageQt import ImageQt
# from PIL.ImageQt import ImageQt

logger = logging.getLogger(__name__)


class Load1jpgPairMixin:  # bridging the view(gui) and the model(data)

    def load_sorted_models(self):
        """This function load the 3d models sorted by how similar they are with respected
        to the selected image.
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        # selected_find = main_model.selected_find
        # We don't allow interactions with the GUI if we are loading the 3d models
        main_presenter.block_signals(True)

        # if selected_find.is_matched:
        #     batch_year, batch_number, batch_piece = selected_find.get_match()
        #     main_view.current_year.setText(str(batch_year))
        #     main_view.current_batch.setText(str(batch_number))
        #     main_view.current_piece.setText(str(batch_piece))
        # else:
        #     main_view.current_year.setText("NS")
        #     main_view.current_batch.setText("NS")
        #     main_view.current_piece.setText("NS")
        #     main_presenter.clean_ply_window()

        # Generate a list of 3d models sorted by similarity.
        # path_2d = main_view.path_2d_picture
        models_sorted_by_similarity = (
            main_presenter.get_potential_3d_models_sorted_by_similarity()
        )

        # Create a new model to contain these
        model = QStandardItemModel(main_view)
        model.setHorizontalHeaderLabels(["Sorted models"])

        # Go through all models, each model represented by a batch, piece and a year
        for batch_num, piece_num, year in models_sorted_by_similarity:
            # If the year is not within the filter, we ignore this 3d model
            if int(year) != int(main_view.year.value()):
                continue

            # If the batch is outside the filter, we ignore this 3d model
            if int(batch_num) < int(main_view.batch_start.value()) or int(
                batch_num
            ) > int(main_view.batch_end.value()):
                continue

            title = year_batch_piece_str(int(year), int(batch_num), int(piece_num))
            # Now the 3d model is guaranteed to be a legitimate one, we add it to the an item
            ply = QStandardItem(title)

            # We check if the 3d model is matched with a find, if it is we set the item to be red
            a3dmodel = main_model.a3dmodels_dict.get(title, None)
            if a3dmodel is None:
                logger.warning("The 3d model %s is not found", title)
                continue
            if a3dmodel.is_matched:
                ply.setForeground(QColor("red"))

            # We save the 3d model path to the item as well
            ply.setData(str(a3dmodel), Qt.UserRole)

            # Finally we add the item to the model
            model.appendRow(ply)

        main_presenter.clean_ply_window()

        # Reset the list that contains the sorted 3d models
        main_view.sorted_model_list.setModel(model)
        main_view.sorted_model_list.selectionModel().currentChanged.connect(
            main_presenter.change_3d_model
        )

        # Reenable interaction with the GUI
        main_presenter.block_signals(False)
