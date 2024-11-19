from pathlib import Path
import re
from PyQt5.QtGui import QStandardItemModel


class ChooseDirectoryMixin:
    def populate_hemispheres(self):
        """Set the select options of hemisphere as the hemispheres in the root folder"""
        main_model, main_view, _ = self.get_model_view_presenter()
        main_view.hemisphere_cb.clear()

        options = main_model.hemisphere_list
        main_view.hemisphere_cb.addItems(options)
        main_view.hemisphere_cb.setCurrentIndex(0 if len(options) > 0 else -1)
        main_view.hemisphere_cb.setEnabled(len(options) > 1)
        self.populate_zones()

    def populate_zones(self):
        """Set the select options of zones as the zones under the current hemisphere"""
        main_model, main_view, _ = self.get_model_view_presenter()
        options = main_model.zone_list
        main_view.zone_cb.clear()
        main_view.zone_cb.addItems(options)
        main_view.zone_cb.setCurrentIndex(main_model.selected_zone_idx)
        main_view.zone_cb.setEnabled(len(options) > 1)
        self.populate_eastings()

    def populate_eastings(self):
        """Set the select options of eastings as the eastings under the current zones"""
        main_model, main_view, _ = self.get_model_view_presenter()
        options = main_model.easting_list
        main_view.easting_cb.clear()
        main_view.easting_cb.addItems(options)
        main_view.easting_cb.setCurrentIndex(main_model.selected_easting_idx)
        main_view.easting_cb.setEnabled(len(options) > 1)
        self.populate_northings()

    def populate_northings(self):
        """Set the select options of northings as the northings under the current eastings"""
        main_model, main_view, _ = self.get_model_view_presenter()
        options = main_model.northing_list
        main_view.northing_cb.clear()
        main_view.northing_cb.addItems(options)
        main_view.northing_cb.setCurrentIndex(main_model.selected_northing_idx)
        main_view.northing_cb.setEnabled(len(options) > 1)
        self.populate_contexts()

    def populate_contexts(self):
        """Set the select options of contexts as the contexts under the current northing"""
        main_model, main_view, _ = self.get_model_view_presenter()
        options = [str(sc.context_number) for sc in main_model.context_list]
        main_view.context_cb.clear()
        main_view.context_cb.addItems(options)
        main_view.context_cb.setCurrentIndex(main_model.selected_context_idx)
        main_view.context_cb.setEnabled(len(options) > 1)

    def on_hemisphere_change(self):
        """This function is called when the user changes the hemisphere select"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        new_index = main_view.hemisphere_cb.currentIndex()
        if new_index != main_model.selected_hemisphere_idx:
            main_model.set_hemisphere_index(new_index)
            main_presenter.populate_zones()
            main_view.contextDisplay.setText(main_presenter.get_context_string())

    def on_zone_change(self):
        """This function is called when the user changes the zone select"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        new_index = main_view.zone_cb.currentIndex()
        if new_index != main_model.selected_zone_idx:
            main_model.set_zone_index(new_index)
            main_presenter.populate_eastings()
            main_view.contextDisplay.setText(main_presenter.get_context_string())

    def on_easting_change(self):
        """This function is called when the user changes the easting select"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        new_index = main_view.easting_cb.currentIndex()
        if new_index != main_model.selected_easting_idx:
            main_model.set_easting_index(new_index)
            main_presenter.populate_northings()
            main_view.contextDisplay.setText(main_presenter.get_context_string())

    def on_northing_change(self):
        """This function is called when the user changes the northing select"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        new_index = main_view.northing_cb.currentIndex()
        if new_index != main_model.selected_northing_idx:
            main_model.set_northing_index(new_index)
            main_presenter.populate_contexts()
            main_view.contextDisplay.setText(main_presenter.get_context_string())

    def on_context_change(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        new_index = main_view.context_cb.currentIndex()
        if new_index != main_model.selected_context_idx:
            main_model.set_context_index(new_index)
            main_view.contextDisplay.setText(main_presenter.get_context_string())
            self.set_filter()

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
