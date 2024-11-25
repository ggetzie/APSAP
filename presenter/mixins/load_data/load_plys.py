import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)

logger = logging.getLogger(__name__)


class LoadPlys:
    def populate_models(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        main_view.clear_unsorted_models()
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
                    logger.debug("Measuring pixels for %s", a3dmodel)
                    main_presenter.measure_pixels_3d(a3dmodel)
                    model_piece = QStandardItem(f"{piece_number}")
                    model_piece.setData(str(a3dmodel), Qt.UserRole)
                    if a3dmodel.is_matched:
                        model_piece.setForeground(QColor("red"))
                    batch_item.appendRow(model_piece)
                year_item.appendRow(batch_item)
            main_view.unsorted_model_list.selectionModel().model().appendRow(year_item)
        main_presenter.block_signals(False)
