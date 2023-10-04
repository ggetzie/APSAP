from PyQt5.QtGui import QStandardItemModel
from pathlib import Path
import re

class ChooseDirectoryMixin:
    def populate_hemispheres(self):
        """Set the select options of hemisphere as the hemispheres in the root folder"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        main_view.hemisphere_cb.clear()

        options = [
            d.name
            for d in main_model.file_root.iterdir()
            if d.name in main_model.path_variables["HEMISPHERES"] and d.is_dir()
        ]
        main_view.hemisphere_cb.addItems(options)
        main_view.hemisphere_cb.setCurrentIndex(0 if len(options) > 0 else -1)
        main_view.hemisphere_cb.setEnabled(len(options) > 1)

    def populate_zones(self):
        """Set the select options of zones as the zones under the current hemisphere"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        if main_view.hemisphere_cb.count() > 0:
            main_view.zone_cb.clear()

            hemisphere = main_view.hemisphere_cb.currentText()
            zone_root = main_model.file_root / hemisphere
            options = main_presenter.get_options(zone_root)
            main_view.zone_cb.addItems(options)

            main_view.zone_cb.setCurrentIndex(0 if len(options) > 0 else -1)
            main_view.zone_cb.setEnabled(len(options) > 1)

    def populate_eastings(self):
        """Set the select options of eastings as the eastings under the current zones"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        if main_view.zone_cb.count() > 0:
            main_view.easting_cb.clear()

            hemisphere = main_view.hemisphere_cb.currentText()
            zone = main_view.zone_cb.currentText()
            eastings_root = main_model.file_root / hemisphere / zone
            options = main_presenter.get_options(eastings_root)
            main_view.easting_cb.addItems(options)

            main_view.easting_cb.setCurrentIndex(0 if len(options) > 0 else -1)
            main_view.easting_cb.setEnabled(len(options) > 1)

    def populate_northings(self):
        """Set the select options of northings as the northings under the current eastings"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        if main_view.easting_cb.count() > 0:
            main_view.northing_cb.clear()

            northings_root = (
                main_model.file_root
                / main_view.hemisphere_cb.currentText()
                / main_view.zone_cb.currentText()
                / main_view.easting_cb.currentText()
            )
            options = main_presenter.get_options(northings_root)

            main_view.northing_cb.addItems(options)
            main_view.northing_cb.setCurrentIndex(0 if len(options) > 0 else -1)
            main_view.northing_cb.setEnabled(len(options) > 1)

    def populate_contexts(self):
        """Set the select options of contexts as the contexts under the current northing"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        if main_view.northing_cb.count() > 0:
            main_view.context_cb.clear()

            contexts_root = (
                main_model.file_root
                / main_view.hemisphere_cb.currentText()
                / main_view.zone_cb.currentText()
                / main_view.easting_cb.currentText()
                / main_view.northing_cb.currentText()
            )
            options = main_presenter.get_options(contexts_root)

            options.sort(key=int)
            main_view.context_cb.addItems(options)

            main_view.context_cb.setCurrentIndex(0 if len(options) > 0 else -1)
            main_view.context_cb.setEnabled(len(options) > 1)

    def clear_interface(self):
        """Clear all the texts, and selects, iamges displayed and 3d models from the interface."""
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        main_view.findFrontPhoto_l.clear()
        main_view.findBackPhoto_l.clear()
        main_view.statusLabel.setText(f"")
        main_view.selected_find.setText(f"")
        main_view.current_batch.setText(f"")
        main_view.current_year.setText(f"")
        main_view.current_piece.setText(f"")
        main_view.new_batch.setText(f"")
        main_view.new_piece.setText(f"")
        main_view.new_year.setText(f"")
        main_view.contextDisplay.setText(self.get_context_string())
        if hasattr(main_view, "current_pcd"):
            main_view.ply_window.remove_geometry(main_view.current_pcd)
            main_view.current_pcd = None

        model = QStandardItemModel(main_view)
        main_view.sorted_model_list.setModel(model)
        main_presenter.reset_ply_selection_model()
        main_view.finds_list.setCurrentItem(None)
        main_view.finds_list.clear()

    def loadImagesPlys(self):
        """This function loads all the finds and models under the current path."""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
         
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
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        hzenc = [
            main_view.hemisphere_cb.currentText(),
            main_view.zone_cb.currentText(),
            main_view.easting_cb.currentText(),
            main_view.northing_cb.currentText(),
            main_view.context_cb.currentText(),
        ]
        return "-".join(hzenc)

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
        except:
            options = []
        return options

    def get_context_dir(self):
        """This function get the whole directory path with all the current selects

        Returns:
            Path(): A Path from pathlib that represents the current path
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()

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
        main_model, view, main_presenter = self.get_model_view_presenter()
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
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        m = re.search(
            main_model.path_variables["MODELS_FILES_RE"],
            path_3d.replace("\\", "/"),
        )
        year = m.group(1)
        batch = m.group(2)
        piece = m.group(3)
        return (year, batch, piece)
