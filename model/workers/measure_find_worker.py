import logging
from typing import List
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from model.models import ObjectFind


logger = logging.getLogger(__name__)


class MeasureFindWorkerSignals(QObject):
    """This class contains the signals that the MeasureFindWorker will emit.

    Args:
        QObject (class): The class that will emit the signals
    """

    progress = pyqtSignal(tuple)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    result = pyqtSignal(str)


class MeasureFindWorker(QRunnable):

    def __init__(
        self,
        object_find_list: List[ObjectFind],
        ceramics_predictor,
        color_grid_predictor,
        cache,
    ):
        super().__init__()
        self.object_find_list = object_find_list
        self.signals = MeasureFindWorkerSignals()
        self.color_grid_predictor = color_grid_predictor
        self.ceramics_predictor = ceramics_predictor
        self.cache = cache

    @pyqtSlot()
    def run(self):
        """This function measures the object find and saves the result to the cache"""
        count = 0
        total = len(self.object_find_list)
        for object_find in self.object_find_list:
            try:
                logger.debug("Measuring object find %s", object_find.find_number)
                object_find.measure(
                    self.ceramics_predictor, self.color_grid_predictor, self.cache
                )
                count += 1
                self.signals.progress.emit(
                    (
                        f"Measured find {object_find.find_number}",
                        int(count / total * 100),
                        object_find.find_number,
                    )
                )
            except Exception as e:
                logger.error(
                    "Failed to measure find %s: %s", object_find.find_number, e
                )
                self.signals.error.emit(
                    f"Failed to measure find {object_find.find_number}"
                )

        self.signals.finished.emit("Finished measuring finds")
