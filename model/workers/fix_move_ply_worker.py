import logging
from pathlib import Path
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from plyfile import PlyData, PlyProperty


class FixMovePlyWorkerSignals(QObject):
    """This class contains the signals that the FileMoveWorker will emit.

    Args:
        QObject (class): The class that will emit the signals
    """

    progress = pyqtSignal(str)
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
        """This function fixes the 3d model from the source path and saves it to the destination path.
        This makes sure the 3d model can be opened with Gilgamesh.

        It fixes the 3d model by replacing the ply file's header's double properties with float properties.

        Args:
            source (str): The url of the source 3d model that may crash Gilgamesh
            target (str): The url of the fixed 3d model
        """
        self.signals.progress.emit("Checking source and destination paths...")
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
        self.signals.progress.emit(f"Reading ply data from {self.source}...")
        ply_data = PlyData.read(self.source)

        self.signals.progress.emit("Fixing ply data...")
        real_properties = []
        for i in ply_data.elements[0].properties:
            if str(PlyProperty(i.name, "double")) == str(i):
                real_properties.append(PlyProperty(i.name, "float32"))
            else:
                real_properties.append(i)

        real_properties = tuple(real_properties)
        ply_data.elements[0].properties = real_properties

        self.signals.progress.emit(f"Writing fixed ply data to {self.destination}...")
        ply_data.write(self.destination)
        self.signals.finished.emit()

    def fix_and_move(self, src, dest):
        pass
