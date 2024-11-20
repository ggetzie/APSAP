from pathlib import Path
import re
from PyQt5.QtGui import QStandardItemModel


class ChooseDirectoryMixin:

    def clear_interface(self):
        """Clear all the texts, and selects, images displayed and 3d models from the interface."""
        _, main_view, main_presenter = self.get_model_view_presenter()

        main_view.findFrontPhoto_l.clear()
        main_view.findBackPhoto_l.clear()
        main_view.statusLabel.setText("")
        main_view.selected_find.setText("")
        main_view.current_batch.setText("")
        main_view.current_year.setText("")
        main_view.current_piece.setText("")
        main_view.new_batch.setText("")
        main_view.new_piece.setText("")
        main_view.new_year.setText("")
        main_view.contextDisplay.setText(self.get_context_string())
        if hasattr(main_view, "current_pcd"):
            main_view.ply_window.remove_geometry(main_view.current_pcd)
            main_view.current_pcd = None

        model = QStandardItemModel(main_view)
        main_view.sorted_model_list.setModel(model)
        main_presenter.reset_ply_selection_model()
        main_view.finds_list.setCurrentItem(None)
        main_view.finds_list.clear()

    def load_images_plys(self):
        """This function loads all the finds and models under the current path."""
        _, main_view, main_presenter = self.get_model_view_presenter()

        self.clear_interface()

        if main_view.context_cb.count() > 0:
            main_presenter.populate_finds()
            main_presenter.populate_models()

    def get_context_string(self):
        """Return a string representing the full designation of the current context
        as utm_hemisphere-utm_zone-utm_easting-utm_northing-context_number

        Returns:
            str: The full designation of the currently selected context
        """
        main_model, _, _ = self.get_model_view_presenter()
        return str(main_model.context_list[main_model.selected_context_idx])

    def get_options(self, path):
        """This function gets all the options of all the subdirectories under the current directory.

        Args:
            path (str): The path under which we search for subdirectories

        Returns:
            list: A list of all the options under the current directory
        """
        try:
            options = [
                d.name for d in path.iterdir() if d.is_dir() and d.name.isdigit()
            ]
        except FileNotFoundError:
            options = []
            options = []
        return options

    def get_context_dir(self):
        """This function get the whole directory path with all the current selects

        Returns:
            Path(): A Path from pathlib that represents the current path
        """
        main_model, main_view, _ = self.get_model_view_presenter()

        res = (
            main_model.file_root
            / main_view.hemisphere_cb.currentText()
            / main_view.zone_cb.currentText()
            / main_view.easting_cb.currentText()
            / main_view.northing_cb.currentText()
            / main_view.context_cb.currentText()
        )
        if not res.exists():
            main_view.statusLabel.setText(f"{res} does not exist!")
            return Path()
        return res

    def get_easting_northing_context(self):
        """This function returns the easting, northing and context

        Returns:
            tuple: The tuple of the easting, northing and context of the current path
        """
        _, _, main_presenter = self.get_model_view_presenter()
        context_dir = main_presenter.get_context_dir()
        (easting, northing, context) = Path(context_dir).parts[-3:]
        return (easting, northing, context)

    def get_year_batch_piece(self, path_3d):
        """This function returns the year, batch, and piece number of a 3d model

        Args:
            path_3d (str): the path of the 3d model

        Returns:
            tuple: The year, batch and piece values to be returned
        """
        main_model, _, _ = self.get_model_view_presenter()

        m = re.search(
            main_model.path_variables["MODELS_FILES_RE"],
            path_3d.replace("\\", "/"),
        )
        year = m.group(1)
        batch = m.group(2)
        piece = m.group(3)
        return (year, batch, piece)
