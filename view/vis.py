import win32gui
import open3d as o3d
from comparator import Comparator
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
import re
from config.path_variables import MODELS_FILES_RE

class Visualized:
    def set_up_3d_window(self):
        widget = self.model

        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(
            visible=False
        )  # Visible false there wont be an extra window opened
        self.comparator = Comparator(self.vis)
        hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")

        self.window = QWindow.fromWinId(hwnd)
        self.windowcontainer = QWidget.createWindowContainer(self.window, widget)
        self.windowcontainer.setMinimumSize(430, 390)

        timer = QTimer(self)
        timer.timeout.connect(self.update_vis)
        timer.start(1)

    def update_vis(self):

        self.vis.poll_events()
        self.vis.update_renderer()

 