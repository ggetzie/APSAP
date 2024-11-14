import logging
from pathlib import Path
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from plyfile import PlyData, PlyProperty


class FixMovePlyWorkerSignals(QObject):
    """This class contains the signals that the FileMoveWorker will emit.

    Args:
        QObject (class): The class that will emit the signals
    """

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class FixMovePlyWorker(QRunnable):

    def __init__(self, source: str, destination: str):
        self.source = source
        self.destination = destination
        self.signals = FixMovePlyWorkerSignals()

    @pyqtSlot()
    def run(self):
        if self.source[-4:] != ".ply" or self.destination[-4:] != ".ply":
            logging.error("Source and self.destination must be valid ply")
            self.signals.error.emit((self.source, self.destination))
            return

        if self.source == self.destination or Path(self.source) == Path(
            self.destination
        ):
            logging.error("Source cannot be the same as self.destination")
            self.signals.error.emit((self.source, self.destination))
            return

        ply_data = PlyData.read(self.source)

        real_properties = []
        for i in ply_data.elements[0].properties:
            if str(PlyProperty(i.name, "double")) == str(i):
                real_properties.append(PlyProperty(i.name, "float32"))
            else:
                real_properties.append(i)

        real_properties = tuple(real_properties)
        ply_data.elements[0].properties = real_properties

        ply_data.write(self.destination)
        self.signals.finished.emit()
