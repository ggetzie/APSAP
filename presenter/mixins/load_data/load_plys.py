import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)
from model.models import year_batch_piece_str

logger = logging.getLogger(__name__)


class LoadPlys:
    def populate_models(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        self.reset_ply_selection_model()
        main_presenter.block_signals(True)
        nested_a3dmodels = main_model.get_nested_a3dmodels()
        filter_year = main_view.year.value()
        min_batch = main_view.batch_start.value()
        max_batch = main_view.batch_end.value()
        for batch_year in sorted(nested_a3dmodels.keys()):
            if batch_year != int(filter_year):
                continue
            year_item = QStandardItem(f"{batch_year}")
            for batch_number in sorted(nested_a3dmodels[batch_year].keys()):
                if int(batch_number) < int(min_batch) or int(batch_number) > int(
                    max_batch
                ):
                    continue
                batch_item = QStandardItem(f"{batch_number}")
                for piece_number in sorted(
                    nested_a3dmodels[batch_year][batch_number].keys()
                ):
                    a3dmodel = nested_a3dmodels[batch_year][batch_number][piece_number]
                    logger.info("Measuring pixels for %s", a3dmodel)
                    main_presenter.measure_pixels_3d(a3dmodel)
                    model_piece = QStandardItem(f"{piece_number}")

                    ply_str = year_batch_piece_str(
                        batch_year, batch_number, piece_number
                    )
                    model_piece.setData(ply_str, Qt.UserRole)
                    if main_model.is_a3dmodel_matched(ply_str):
                        model_piece.setForeground(QColor("red"))
                    batch_item.appendRow(model_piece)
                year_item.appendRow(batch_item)
            main_view.modelList.selectionModel().model().appendRow(year_item)
        main_presenter.block_signals(False)

    def reset_ply_selection_model(self):
        """This function ensures that there is a empty modelList
        in the view
        """
        _, main_view, main_presenter = self.get_model_view_presenter()

        # We create a new modelList's selection model if there isn't one
        if not main_view.modelList.selectionModel():
            model = QStandardItemModel(main_view)
            model.setHorizontalHeaderLabels(["Models"])
            main_view.modelList.setModel(model)
            main_view.modelList.selectionModel().currentChanged.connect(
                main_presenter.change_3d_model
            )
        else:
            # Otherwise we empty the list
            main_view.modelList.selectionModel().model().removeRows(
                0, main_view.modelList.selectionModel().model().rowCount()
            )
