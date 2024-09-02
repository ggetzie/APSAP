import logging

import win32gui
import open3d as o3d
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, QCoreApplication


class PlyWindowMixin:
    def set_up_ply_window(self):
        """This function set up the window that displays the point cloud ply fie."""
        # 0. Get the widget that we want to display our 3d model in
        widget = self.model

        # 1. Setting up a window of Open3d to display the 3d model
        self.ply_window = o3d.visualization.Visualizer()
        self.ply_window.create_window(visible=False)
        self.ply_window.get_render_option().light_on = False
        self.ply_window.get_render_option().point_size = 20

        # 2.Attaching the open3d window we just created to our application
        hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")
        window = QWindow.fromWinId(hwnd)
        window_container = QWidget.createWindowContainer(window, widget)
        window_container.setMinimumSize(430, 390)

        timer = QTimer(self)
        timer.timeout.connect(self.update_ply_window)
        timer.start(100)

    def update_ply_window(self):
        """This function periodically updates the little window that displays the 3d model"""
        self.ply_window.poll_events()
        self.ply_window.update_renderer()
