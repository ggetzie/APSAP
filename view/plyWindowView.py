import win32gui
import open3d as o3d
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer

class PlyWindowView:

    def setUpPlyWindow(self):
        widget = self.model

        #This creates a window that shows the 3d model in ply format
        self.plyWindow = o3d.visualization.Visualizer()
        self.plyWindow.create_window(visible=False)   
      
        #This fixes the ply window inside the mainWindow
        hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")
        window = QWindow.fromWinId(hwnd)
        windowcontainer = QWidget.createWindowContainer(window, widget)
        windowcontainer.setMinimumSize(430, 390)

        #Contiously update the open3d ply window
        timer = QTimer(self)
        timer.timeout.connect(self.updatePlyWindow)
        timer.start(1)

    def updatePlyWindow(self):

        self.plyWindow.poll_events()
        self.plyWindow.update_renderer()

 