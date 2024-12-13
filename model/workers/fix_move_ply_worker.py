import logging
from pathlib import Path
from typing import List, Tuple
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from plyfile import PlyData, PlyProperty


class FixMovePlyWorkerSignals(QObject):
    """This class contains the signals that the FileMoveWorker will emit.

    Args:
        QObject (class): The class that will emit the signals
    """

    progress = pyqtSignal(tuple)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    result = pyqtSignal(str)


class FixMovePlyWorker(QRunnable):

    def __init__(
        self,
        source_dest_pairs: List[Tuple[Path, Path]],
        model_str: str,
        find_number: int,
    ):
        super().__init__()
        self.source_dest_pairs = source_dest_pairs
        self.model_str = model_str
        self.find_number = find_number
        self.signals = FixMovePlyWorkerSignals()

    @pyqtSlot()
    def run(self):
        count = 0
        total = len(self.source_dest_pairs)
        for source, destination in self.source_dest_pairs:
            msg = f"Moving {self.model_str} {source.name} to find {self.find_number} as {destination.name}"
            self.signals.progress.emit((msg, int(count / total * 100)))
            self.move_pair(source, destination)
            count += 1
        self.signals.finished.emit(
            f"Moved ply files for {self.model_str} to find {self.find_number}"
        )

    def move_pair(self, source: Path, destination: Path):
        """This function fixes the 3d model from the source path and saves it to the destination path.
        This makes sure the 3d model can be opened with Gilgamesh.

        It fixes the 3d model by replacing the ply file's header's double properties with float properties.

        Args:
            source (str): The url of the source 3d model that may crash Gilgamesh
            target (str): The url of the fixed 3d model
        """

        if source.suffix != ".ply" or destination.suffix != ".ply":
            msg = "Source and self.destination must be valid ply"
            logging.error(msg)
            self.signals.error.emit(msg)
            return

        if source == destination:
            msg = "Source cannot be the same as destination"
            logging.error(msg)
            self.signals.error.emit(msg)
            return
        ply_data = PlyData.read(str(source))

        real_properties = []
        for i in ply_data.elements[0].properties:
            if str(PlyProperty(i.name, "double")) == str(i):
                real_properties.append(PlyProperty(i.name, "float32"))
            else:
                real_properties.append(i)

        real_properties = tuple(real_properties)
        ply_data.elements[0].properties = real_properties

        ply_data.write(str(destination))
