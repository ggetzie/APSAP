import open3d as o3d
from PyQt5.QtCore import Qt
import re


class Display3dModelControllerMixin:
    def __init__(self):
        pass


    def change_model(self, current_pcd, previous_pcd):
        mainModel, mainView, mainController = self.get_model_view_controller()
        mainView.plyWindow.get_render_option().point_size = (
            5  # Generally we need this value to be larger only if we draw the jpgs
        )
        if previous_pcd:
            mainView.plyWindow.remove_geometry(previous_pcd)
        mainView.current_pcd = current_pcd
        mainView.plyWindow.add_geometry(current_pcd)
        mainView.plyWindow.update_geometry(current_pcd)

    def change_3d_model(self, current, previous):
        mainModel, mainView, mainController = self.get_model_view_controller()
        current_model_path = current.data(Qt.UserRole)

        if current_model_path:
            mainView.path_3d_model = current_model_path
            current_pcd_load = o3d.io.read_point_cloud(current_model_path)
            if not hasattr(mainView, "current_pcd"):
                mainView.current_pcd = None
            mainController.change_model(current_pcd_load, mainView.current_pcd)
            mainView.current_pcd = current_pcd_load

            m = re.search(mainModel.path_variables["MODELS_FILES_RE"], current_model_path.replace("\\", "/"))
            # This error happens when the relative path is different
            if m:
              
                batch_num = str(
                    int(m.group(1))
                )  # int("006") -> int(6). We remove leading 0
                piece_num = m.group(2)
                mainView.new_batch.setText(batch_num)
                mainView.new_piece.setText(piece_num)

