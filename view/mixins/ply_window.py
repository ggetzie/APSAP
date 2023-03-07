import win32gui
import open3d as o3d
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer

class PlyWindowMixin:

    def set_up_ply_window(self):
        widget = self.model

        self.ply_window = o3d.visualization.Visualizer()
        self.ply_window.create_window(visible=False)   
        self.ply_window.get_render_option().light_on = False
        self.ply_window.get_render_option().point_size = 20 
                  
        hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")
        window = QWindow.fromWinId(hwnd)
        windowcontainer = QWidget.createWindowContainer(window, widget)
        windowcontainer.setMinimumSize(430, 390)

        timer = QTimer(self)
        timer.timeout.connect(self.update_ply_window)
        timer.start(1)
        
    def update_ply_window(self):

        self.ply_window.poll_events()
        self.ply_window.update_renderer()

 