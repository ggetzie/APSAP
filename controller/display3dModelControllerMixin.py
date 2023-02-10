import win32gui
import open3d as o3d
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer
import re
from configs.path_variables import MODELS_FILES_RE


class Display3dModelControllerMixin:
    def __init__(self):
        pass


    def change_model(self, current_pcd, previous_pcd):
        mainModel, view, controller = self.get_model_view_controller()
        view.plyWindow.get_render_option().point_size = (
            5  # Generally we need this value to be larger only if we draw the jpgs
        )
        if previous_pcd:
            view.plyWindow.remove_geometry(previous_pcd)
        view.current_pcd = current_pcd
        view.plyWindow.add_geometry(current_pcd)
        view.plyWindow.update_geometry(current_pcd)

    def change_3d_model(self, current, previous):
        mainModel, view, controller = self.get_model_view_controller()
        current_model_path = current.data(Qt.UserRole)

        if current_model_path:
            view.path_3d_model = current_model_path
            current_pcd_load = o3d.io.read_point_cloud(current_model_path)
            if not hasattr(view, "current_pcd"):
                view.current_pcd = None
            controller.change_model(current_pcd_load, view.current_pcd)
            view.current_pcd = current_pcd_load

            m = re.search(MODELS_FILES_RE, current_model_path.replace("\\", "/"))
            # This error happens when the relative path is different
            if m:
              
                batch_num = str(
                    int(m.group(1))
                )  # int("006") -> int(6). We remove leading 0
                piece_num = m.group(2)
                view.new_batch.setText(batch_num)
                view.new_piece.setText(piece_num)

