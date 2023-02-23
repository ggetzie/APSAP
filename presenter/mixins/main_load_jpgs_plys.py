from pathlib import Path
from presenter.mixins.load_jpgs_plys.load_jpgs import LoadJpgs
from presenter.mixins.load_jpgs_plys.load_plys import LoadPlys

class LoadJpgsPlysMixin(LoadJpgs, LoadPlys):
    def get_context_dir(self):
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
        main_model, view, main_presenter = self.get_model_view_presenter()

        context_dir = main_presenter.get_context_dir()
        path_parts = Path(context_dir).parts[-3:]
        easting = int(path_parts[0])
        northing = int(path_parts[1])
        context = int(path_parts[2])

        return (easting, northing, context)


