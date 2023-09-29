import win32gui
import open3d as o3d
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer


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
        windowcontainer = QWidget.createWindowContainer(window, widget)
        windowcontainer.setMinimumSize(430, 390)

        timer = QTimer(self)
        timer.timeout.connect(self.update_ply_window)
        timer.start(1)

    def update_ply_window(self):
        """This function periodically updates the little window that displays the 3d model"""
        self.ply_window.poll_events()
        self.ply_window.update_renderer()

    def blockSignals(self, boolean):
        """This function disables or enables all the interative elements from the GUI when certain oprations are being done
        at the moment

        Args:
            boolean (boolean): True means we disable interaction, False means we enable interaction
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        main_view.hemisphere_cb.setDisabled(boolean)
        main_view.zone_cb.setDisabled(boolean)
        main_view.easting_cb.setDisabled(boolean)
        main_view.northing_cb.setDisabled(boolean)
        main_view.context_cb.setDisabled(boolean)

        main_view.finds_list.setDisabled(boolean)

        main_view.batch_start.setDisabled(boolean)
        main_view.batch_end.setDisabled(boolean)
        main_view.find_start.setDisabled(boolean)
        main_view.find_end.setDisabled(boolean)

        main_view.loadAll.setDisabled(boolean)

        main_view.update_button.setDisabled(boolean)
        main_view.remove_button.setDisabled(boolean)

        main_view.modelList.setDisabled(boolean)
        main_view.sorted_model_list.setDisabled(boolean)

        main_view.year.setDisabled(boolean)