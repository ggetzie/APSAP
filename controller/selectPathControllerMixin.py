
from PyQt5.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)
import time
from PyQt5.QtGui import (
    QStandardItemModel,
)
from PyQt5.QtCore import Qt

from config.path_variables import (
    FINDS_SUBDIR,
    FINDS_PHOTO_DIR,
    MODELS_FILES_DIR,
    MODELS_FILES_RE,
)

#This class contains classes and functiosn related to functionalities related to pop_up
from PyQt5.QtWidgets import QMainWindow, QSplashScreen

class LoadingSplash(QSplashScreen):
    
    def mousePressEvent(self, event):
            
        pass

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

        controller.contextChanged()

    def contextChanged(self):
        mainModel, view, controller = self.get_model_view_controller()

        view.statusLabel.setText(f"")
        view.selected_find.setText(f"")
        view.current_batch.setText(f"")
        view.current_piece.setText(f"")
        view.new_batch.setText(f"")
        view.new_piece.setText(f"")
        view.contextDisplay.setText(self.get_context_string())
        if hasattr(view, "current_pcd"):
            view.vis.remove_geometry(view.current_pcd)
            view.current_pcd = None

        model = QStandardItemModel(view)
        view.sortedModelList.setModel(model)
        funcs_to_run = [
            ["Loading finds. It might take a while", controller.populate_finds],
            ["Loading models. It might take a while", controller.populate_models],
        ]

        now = time.time()
        controller.load_and_run(funcs_to_run)
        print(f"Timed passed: {time.time() - now} seconds")



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


    def load_and_run(self, funcs_to_run):
        #Load the splash
        splash = LoadingSplash()
        splash.show()
        #Run all functions and the message during loading time
        for message_func in funcs_to_run:
            message = message_func[0]
            func = message_func[1]
            splash.showMessage(message)
            func()
        #Close the window    
        window = QMainWindow()
        window.show()
        splash.finish(window)
      
    