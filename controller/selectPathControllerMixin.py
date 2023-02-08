
from config.path_variables import FINDS_SUBDIR, BATCH_3D_SUBDIR, FINDS_PHOTO_DIR, MODELS_FILES_DIR, MODELS_FILES_RE, HEMISPHERES
from functools import partial


class SelectPathControllerMixin: #bridging the view(gui) and the model(data)

    def __init__(self, view, model):
        #Notice this object is the controller, that which connects the view(GUI) and the model(data)
        controller = self
        self.populate_hemispheres()

        #Here we connect the view with the control of mouse clicks and selects
        view.hemisphere_cb.currentIndexChanged.connect( controller.populate_zones)
        view.zone_cb.currentIndexChanged.connect(controller.populate_eastings)
        view.easting_cb.currentIndexChanged.connect(controller.populate_northings)
        view.northing_cb.currentIndexChanged.connect( (controller.populate_contexts))
        view.context_cb.currentIndexChanged.connect(controller.contextChanged)


    def populate_hemispheres(self): 
        #Getting m, v, c from to update the gui and get the data.
        model, view, controller = self.get_model_view_controller()
        
        #Clear the combox box
        view.hemisphere_cb.clear()
        
        #Get the hemispheres and add it to the combo box
        res = model.get_hemispheres()
        view.hemisphere_cb.addItems(res)

        #Set the index of the select as 0 by default and allow the select to be "selected"  if there are more than 1 elements 
        view.hemisphere_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        view.hemisphere_cb.setEnabled(len(res) > 1)

        #This is important. The hierarchy is hemispheres, zones, eastings, northings, contexts, finds/models
        #When the former one is populated, ther ones after that are populated one by one til the end of the chain.
        controller.populate_zones()


    def populate_zones(self ):
        #Check populate_zones for explanations
        model, view, controller = self.get_model_view_controller()

        view.zone_cb.clear()

        hemisphere = view.hemisphere_cb.currentText()
        zone_root = model.file_root / hemisphere
        res = model.get_options(zone_root)
        view.zone_cb.addItems(res)

        view.zone_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        view.zone_cb.setEnabled(len(res) > 1)

        controller.populate_eastings()
 
    def populate_eastings(self):
        #Check populate_zones for explanations
        model, view, controller = self.get_model_view_controller()

        view.easting_cb.clear()

        hemisphere = view.hemisphere_cb.currentText()
        zone = view.zone_cb.currentText()
        eastings_root = model.file_root / hemisphere / zone
        res = model.get_options(eastings_root)
        view.easting_cb.addItems(res)

        view.easting_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        view.easting_cb.setEnabled(len(res) > 1)

        controller.populate_northings()

    def populate_northings(self):
        #Check populate_zones for explanations
        model, view, controller = self.get_model_view_controller()

        view.northing_cb.clear()

        northings_root = (
            model.file_root
            / view.hemisphere_cb.currentText()
            / view.zone_cb.currentText()
            / view.easting_cb.currentText()
        )
        res = model.get_options(northings_root)
        view.northing_cb.addItems(res)

        view.northing_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        view.northing_cb.setEnabled(len(res) > 1)

        controller.populate_contexts()

    def populate_contexts(self):
        #Check populate_zones for explanations,  except this "populate" function takes the final functions populate_finds and populate_models in a load_and_run mechanism that shows
        model, view, controller = self.get_model_view_controller()

        view.context_cb.clear()

        contexts_root = (
            model.file_root
            / view.hemisphere_cb.currentText()
            / view.zone_cb.currentText()
            / view.easting_cb.currentText()
            / view.northing_cb.currentText()
        )
        res = model.get_options(contexts_root)  
        res.sort(key=int)
        view.context_cb.addItems(res)

        view.context_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        view.context_cb.setEnabled(len(res) > 1)

        #Using these lines we print the progress when we load the finds and models, which takes considerable amount of time
        funcs_to_run = [
            ["Loading finds. It might take a while", view.populate_finds],
            ["Loading models. It might take a while", view.populate_models],
        ]
        view.load_and_run(funcs_to_run)



    def get_context_string(self):
        """Return a string representing the full designation of the current context
        as utm_hemisphere-utm_zone-utm_easting-utm_northing-context_number

        Returns:
            str: The full designation of the currently selected context
        """
        model, view, controller = self.get_model_view_controller()

        hzenc = [
            view.hemisphere_cb.currentText(),
            view.zone_cb.currentText(),
            view.easting_cb.currentText(),
            view.northing_cb.currentText(),
            view.context_cb.currentText(),
        ]
        return "-".join(hzenc)
 