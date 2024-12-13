import time
from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot


class TestWorkerSignals(QObject):
    """This class contains the signals that the FileMoveWorker will emit.

    Args:
        QObject (class): The class that will emit the signals
    """

    progress = pyqtSignal(tuple)  # send a tuple of (str, int) to show progress
    finished = pyqtSignal(str)
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class TestWorker(QRunnable):

    def __init__(self):
        super().__init__()
        self.signals = TestWorkerSignals()

    @pyqtSlot()
    def run(self):
        """This function tests the worker by emitting a progress signal every second"""
        for i in range(1, 11):
            self.signals.progress.emit((f"Progress: {i * 10}%", i * 10))
            time.sleep(1)
        self.signals.finished.emit("Finished testing worker")
