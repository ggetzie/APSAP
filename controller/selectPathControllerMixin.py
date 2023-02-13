import time
from PyQt5.QtGui import (
    QStandardItemModel,
)

from PyQt5.QtWidgets import QMainWindow, QSplashScreen

class LoadingSplash(QSplashScreen):
    
    def mousePressEvent(self, event):
            
        pass

class SelectPathControllerMixin: #bridging the view(gui) and the model(data)

    def __init__(self, view, model):
        #Notice this object is the controller, that which connects the view(GUI) and the model(data)
        controller = self
        self.populate_hemispheres()




    def populate_hemispheres(self): 
        #Getting m, v, c from to update the gui and get the data.
        mainModel, mainView, mainController = self.get_model_view_controller()
        
        #Clear the combox box
        mainView.hemisphere_cb.clear()
        
        #Get the hemispheres and add it to the combo box
        res = mainController.get_hemispheres()
        mainView.hemisphere_cb.addItems(res)

        #Set the index of the select as 0 by default and allow the select to be "selected"  if there are more than 1 elements 
        mainView.hemisphere_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        mainView.hemisphere_cb.setEnabled(len(res) > 1)

        #This is important. The hierarchy is hemispheres, zones, eastings, northings, contexts, finds/models
        #When the former one is populated, ther ones after that are populated one by one til the end of the chain.
        mainController.populate_zones()


    def populate_zones(self ):
        #Check populate_zones for explanations
        mainModel, mainView, mainController = self.get_model_view_controller()

        mainView.zone_cb.clear()

        hemisphere = mainView.hemisphere_cb.currentText()
        zone_root = mainModel.file_root / hemisphere
        res = mainController.get_options(zone_root)
        mainView.zone_cb.addItems(res)

        mainView.zone_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        mainView.zone_cb.setEnabled(len(res) > 1)

        mainController.populate_eastings()
 
    def populate_eastings(self):
        #Check populate_zones for explanations
        mainModel, mainView, mainController = self.get_model_view_controller()

        mainView.easting_cb.clear()

        hemisphere = mainView.hemisphere_cb.currentText()
        zone = mainView.zone_cb.currentText()
        eastings_root = mainModel.file_root / hemisphere / zone
        res = mainController.get_options(eastings_root)
        mainView.easting_cb.addItems(res)

        mainView.easting_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        mainView.easting_cb.setEnabled(len(res) > 1)

        mainController.populate_northings()

    def populate_northings(self):
        #Check populate_zones for explanations
        mainModel, mainView, mainController = self.get_model_view_controller()

        mainView.northing_cb.clear()

        northings_root = (
            mainModel.file_root
            / mainView.hemisphere_cb.currentText()
            / mainView.zone_cb.currentText()
            / mainView.easting_cb.currentText()
        )
        res = mainController.get_options(northings_root)
        mainView.northing_cb.addItems(res)
        mainView.northing_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        mainView.northing_cb.setEnabled(len(res) > 1)

        mainController.populate_contexts()

    def populate_contexts(self):
        #Check populate_zones for explanations,  except this "populate" function takes the final functions populate_finds and populate_models in a load_and_run mechanism that shows
        mainModel, mainView, mainController = self.get_model_view_controller()

        mainView.context_cb.clear()

        contexts_root = (
            mainModel.file_root
            / mainView.hemisphere_cb.currentText()
            / mainView.zone_cb.currentText()
            / mainView.easting_cb.currentText()
            / mainView.northing_cb.currentText()
        )
        res = mainController.get_options(contexts_root)  
        res.sort(key=int)
        mainView.context_cb.addItems(res)

        mainView.context_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        mainView.context_cb.setEnabled(len(res) > 1)

        mainController.contextChanged()

    def contextChanged(self):
        mainModel, mainView, mainController = self.get_model_view_controller()

        mainView.statusLabel.setText(f"")
        mainView.selected_find.setText(f"")
        mainView.current_batch.setText(f"")
        mainView.current_piece.setText(f"")
        mainView.new_batch.setText(f"")
        mainView.new_piece.setText(f"")
        mainView.contextDisplay.setText(self.get_context_string())
        if hasattr(mainView, "current_pcd"):
            mainView.plyWindow.remove_geometry(mainView.current_pcd)
            mainView.current_pcd = None

        model = QStandardItemModel(mainView)
        mainView.sortedModelList.setModel(model)
        funcs_to_run = [
            ["Loading finds. It might take a while", mainController.populate_finds],
            ["Loading models. It might take a while", mainController.populate_models],
        ]

        now = time.time()
        mainController.load_and_run(funcs_to_run)
        print(f"Timed passed: {time.time() - now} seconds")

    def get_context_string(self):
        """Return a string representing the full designation of the current context
        as utm_hemisphere-utm_zone-utm_easting-utm_northing-context_number

        Returns:
            str: The full designation of the currently selected context
        """
        mainModel, mainView, mainController = self.get_model_view_controller()

        hzenc = [
            mainView.hemisphere_cb.currentText(),
            mainView.zone_cb.currentText(),
            mainView.easting_cb.currentText(),
            mainView.northing_cb.currentText(),
            mainView.context_cb.currentText(),
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
      

    def get_hemispheres(self):
        mainModel, mainView, mainController = self.get_model_view_controller()

        hemispheres = [
            d.name
            for d in mainModel.file_root.iterdir()
            if d.name in mainModel.path_variables["HEMISPHERES"] and d.is_dir()
        ]
 
        return hemispheres


    def get_options(self, path):
        res = [d.name for d in path.iterdir() if d.is_dir() and d.name.isdigit()]
        return res

