import logging
import open3d as o3d
from PyQt5.QtCore import Qt

logger = logging.getLogger(__name__)


class Load3dModelToWindowMixin:
    """This mixin is about "Loading 3d model into the ply Window" """

    def clean_ply_window(self):
        """This function removes any existent 3d model in the ply window"""
        _, main_view, _ = self.get_model_view_presenter()

        main_view.current_pcd = None
        main_view.ply_window.clear_geometries()

    def change_3d_model(self, current):
        """This function changes the 3d model currently displayed in the ply window

        Args:
            current (object): The current selected item in the 3d model
        """
        _, main_view, main_presenter = self.get_model_view_presenter()
        # Get the saved path in the selected item
        ply_str = current.data(Qt.UserRole)
        self.main_model.select_a3dmodel(ply_str)
        a3dmodel = self.main_model.selected_a3dmodel
        if a3dmodel is None:
            logger.error("The 3d model %s is not found", ply_str)
            return
        current_model_path = a3dmodel.get_file("sample")
        logger.info("Current model path: %s", current_model_path)

        # If the path exists, we try to read it and display it
        if current_model_path:

            # Load the 3d model and set the scene
            current_pcd_load = o3d.io.read_point_cloud(str(current_model_path))
            main_view.ply_window.get_render_option().point_size = 5
            # If there is a 3d model previously, we remove it
            main_presenter.clean_ply_window()
            # We add the 3d model and display it.
            main_view.current_pcd = current_pcd_load
            main_view.ply_window.add_geometry(main_view.current_pcd)
            main_view.ply_window.update_geometry(main_view.current_pcd)

            # We get the 3d model's information (year, batch, piece number) and display them
            # (year, batch, piece) = main_presenter.get_year_batch_piece(
            #     current_model_path
            # )
            main_view.new_year.setText(f"{a3dmodel.batch_year}")
            main_view.new_batch.setText(f"{a3dmodel.batch_number:>03}")
            main_view.new_piece.setText(f"{a3dmodel.batch_piece:>02}")
