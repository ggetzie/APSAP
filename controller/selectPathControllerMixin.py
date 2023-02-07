
from config.path_variables import FINDS_SUBDIR, BATCH_3D_SUBDIR, FINDS_PHOTO_DIR, MODELS_FILES_DIR, MODELS_FILES_RE, HEMISPHERES


class SelectPathControllerMixin: #bridging the view(gui) and the model(data)

    def __init__(self, view, model):

        self.contextDisplay = view.contextDisplay
        self.file_root = view.file_root
        self.model = model
        self.hemisphere_cb = view.hemisphere_cb
        self.zone_cb = view.zone_cb
        self.easting_cb = view.easting_cb
        self.northing_cb = view.northing_cb
        self.hemisphere_cb = view.hemisphere_cb
        self.context_cb = view.context_cb



        self.populate_finds = view.populate_finds
        self.populate_models = view.populate_models
        self.load_and_run = view.load_and_run
        self.contextChanged = view.contextChanged
        self.populate_hemispheres(view, model)

        #Here we connect the view with the control of mouse clicks and selects
        self.hemisphere_cb.currentIndexChanged.connect(lambda: self.populate_zones(view, model))
        self.zone_cb.currentIndexChanged.connect(self.populate_eastings)
        self.easting_cb.currentIndexChanged.connect(self.populate_northings)
        self.northing_cb.currentIndexChanged.connect(self.populate_contexts)
        self.context_cb.currentIndexChanged.connect(self.contextChanged)
        self.contextDisplay.setText(self.get_context_string())

    def populate_hemispheres(self, view, model): 
        view.hemisphere_cb.clear()
        res = model.get_hemispheres()
        view.hemisphere_cb.addItems(res)
        self.set_hemisphere(0 if len(res) > 0 else -1, view, model)
        view.hemisphere_cb.setEnabled(len(res) > 1)
        self.contextDisplay.setText(self.get_context_string())

    def set_hemisphere(self, index, view, model):
        view.hemisphere_cb.setCurrentIndex(index)
        self.populate_zones(view, model)


    def populate_zones(self, view, model):
        view.zone_cb.clear()
        hemisphere = view.hemisphere_cb.currentText()
        zone_root = view.file_root / hemisphere
        res = model.get_zones(zone_root)
        view.zone_cb.addItems(res)
        view.zone_cb.setEnabled(len(res) > 1)
        self.set_zone(0 if len(res) > 0 else -1, view, model)

    def set_zone(self, index, view, model):
        view.zone_cb.setCurrentIndex(index)
        self.populate_eastings(view, model)

    def populate_eastings(self, videw, model):
        self.easting_cb.clear()
        hemisphere = self.hemisphere_cb.currentText()
        zone = self.zone_cb.currentText()
        eastings_root = self.file_root / hemisphere / zone
        res = [
            d.name for d in eastings_root.iterdir() if d.is_dir() and d.name.isdigit()
        ]
        self.easting_cb.addItems(res)
        self.set_easting(0 if len(res) > 0 else -1)
        self.easting_cb.setEnabled(len(res) > 1)

    def set_easting(self, index):
        self.easting_cb.setCurrentIndex(index)
        self.populate_northings()

    def populate_northings(self):
        self.northing_cb.clear()
        northings_root = (
            self.file_root
            / self.hemisphere_cb.currentText()
            / self.zone_cb.currentText()
            / self.easting_cb.currentText()
        )
        res = [
            d.name for d in northings_root.iterdir() if d.is_dir() and d.name.isdigit()
        ]
        self.northing_cb.addItems(res)
        self.set_northing(0 if len(res) > 0 else -1)
        self.northing_cb.setEnabled(len(res) > 1)

    def set_northing(self, index):
        self.northing_cb.setCurrentIndex(index)
        self.populate_contexts()

    def populate_contexts(self):
        self.context_cb.clear()
        contexts_root = (
            self.file_root
            / self.hemisphere_cb.currentText()
            / self.zone_cb.currentText()
            / self.easting_cb.currentText()
            / self.northing_cb.currentText()
        )
        res = [
            d.name for d in contexts_root.iterdir() if d.is_dir() and d.name.isdigit()
        ]
        res.sort(key=int)
        self.context_cb.addItems(res)
        self.set_context(0 if len(res) > 0 else -1)
        self.context_cb.setEnabled(len(res) > 1)
        self.contextChanged()

    def set_context(self, index):
        self.context_cb.setCurrentIndex(index)

    def get_context_string(self):
        """Return a string representing the full designation of the current context
        as utm_hemisphere-utm_zone-utm_easting-utm_northing-context_number

        Returns:
            str: The full designation of the currently selected context
        """
        hzenc = [
            self.hemisphere_cb.currentText(),
            self.zone_cb.currentText(),
            self.easting_cb.currentText(),
            self.northing_cb.currentText(),
            self.context_cb.currentText(),
        ]
        return "-".join(hzenc)
     