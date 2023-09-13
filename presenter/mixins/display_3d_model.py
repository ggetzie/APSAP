import open3d as o3d
from PyQt5.QtCore import Qt
import re


class Display3dModelMixin:

    def change_model(self, current_pcd, previous_pcd):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        main_view.ply_window.get_render_option().point_size = (
            5  # Generally we need this value to be larger only if we draw the jpgs
        )
        if previous_pcd:
            main_view.ply_window.remove_geometry(previous_pcd)
        main_view.current_pcd = current_pcd
        main_view.ply_window.add_geometry(current_pcd)
        main_view.ply_window.update_geometry(current_pcd)

    def change_3d_model(self, current, previous):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        current_model_path = current.data(Qt.UserRole)

        if current_model_path:
            #main_view.path_3d_model = current_model_path
            current_pcd_load = o3d.io.read_point_cloud(current_model_path)
            if not hasattr(main_view, "current_pcd"):
                main_view.current_pcd = None
            main_presenter.change_model(current_pcd_load, main_view.current_pcd)
            main_view.current_pcd = current_pcd_load

            m = re.search(
                main_model.path_variables["MODELS_FILES_RE"],
                current_model_path.replace("\\", "/"),
            )
            # This error happens when the relative path is different
            if m:
                batch_year = str(m.group(1))
                batch_num = str(
                    int(m.group(2))
                )   
                piece_num = m.group(3)
                main_view.new_batch.setText(batch_num)
                main_view.new_piece.setText(piece_num)
                main_view.new_year.setText(batch_year)
