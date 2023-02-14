import win32gui
import open3d as o3d
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer

class PlyWindowMixin:

    def set_up_ply_window(self):
        #Notice this model is a QTWidget instead of our model in the architecture
        widget = self.model

        #This creates a window that shows the 3d model in ply format
        self.ply_window = o3d.visualization.Visualizer()
        self.ply_window.create_window(visible=False)   
        self.ply_window.get_render_option().light_on = False
        self.ply_window.get_render_option().point_size = 20 #If the point is too small, the picture taken will have a lot of holes
                                            #When we use our own field of view      
        #This fixes the ply window inside the mainWindow
        hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")
        window = QWindow.fromWinId(hwnd)
        windowcontainer = QWidget.createWindowContainer(window, widget)
        windowcontainer.setMinimumSize(430, 390)

        #Contiously update the open3d ply window
        timer = QTimer(self)
        timer.timeout.connect(self.update_ply_window)
        timer.start(1)

    def update_ply_window(self):

        self.ply_window.poll_events()
        self.ply_window.update_renderer()

 