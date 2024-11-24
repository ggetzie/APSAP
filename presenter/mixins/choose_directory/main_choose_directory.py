from pathlib import Path
import re

# from PyQt5.QtGui import QStandardItemModel


class ChooseDirectoryMixin:

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
