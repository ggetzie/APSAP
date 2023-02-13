import time
from PyQt5.QtGui import (
    QStandardItemModel,
)

from PyQt5.QtWidgets import QMainWindow, QSplashScreen

class LoadingSplash(QSplashScreen):
    
    def mousePressEvent(self, event):
            
        pass

class SelectPathMixin: #bridging the view(gui) and the model(data)

    def __init__(self, view, model):
        #Notice this object is the controller, that which connects the view(GUI) and the model(data)
        controller = self
        self.populate_hemispheres()




    def populate_hemispheres(self): 
        #Getting m, v, c from to update the gui and get the data.
        main_model, main_view, main_controller = self.get_model_view_controller()
        
        #Clear the combox box
        main_view.hemisphere_cb.clear()
        
        #Get the hemispheres and add it to the combo box
        res = main_controller.get_hemispheres()
        main_view.hemisphere_cb.addItems(res)

        #Set the index of the select as 0 by default and allow the select to be "selected"  if there are more than 1 elements 
        main_view.hemisphere_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        main_view.hemisphere_cb.setEnabled(len(res) > 1)

        #This is important. The hierarchy is hemispheres, zones, eastings, northings, contexts, finds/models
        #When the former one is populated, ther ones after that are populated one by one til the end of the chain.
        main_controller.populate_zones()


    def populate_zones(self ):
        #Check populate_zones for explanations
        main_model, main_view, main_controller = self.get_model_view_controller()

        main_view.zone_cb.clear()

        hemisphere = main_view.hemisphere_cb.currentText()
        zone_root = main_model.file_root / hemisphere
        res = main_controller.get_options(zone_root)
        main_view.zone_cb.addItems(res)

        main_view.zone_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        main_view.zone_cb.setEnabled(len(res) > 1)

        main_controller.populate_eastings()
 
    def populate_eastings(self):
        #Check populate_zones for explanations
        main_model, main_view, main_controller = self.get_model_view_controller()

        main_view.easting_cb.clear()

        hemisphere = main_view.hemisphere_cb.currentText()
        zone = main_view.zone_cb.currentText()
        eastings_root = main_model.file_root / hemisphere / zone
        res = main_controller.get_options(eastings_root)
        main_view.easting_cb.addItems(res)

        main_view.easting_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        main_view.easting_cb.setEnabled(len(res) > 1)

        main_controller.populate_northings()

    def populate_northings(self):
        #Check populate_zones for explanations
        main_model, main_view, main_controller = self.get_model_view_controller()

        main_view.northing_cb.clear()

        northings_root = (
            main_model.file_root
            / main_view.hemisphere_cb.currentText()
            / main_view.zone_cb.currentText()
            / main_view.easting_cb.currentText()
        )
        res = main_controller.get_options(northings_root)
        main_view.northing_cb.addItems(res)
        main_view.northing_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        main_view.northing_cb.setEnabled(len(res) > 1)

        main_controller.populate_contexts()

    def populate_contexts(self):
        #Check populate_zones for explanations,  except this "populate" function takes the final functions populate_finds and populate_models in a load_and_run mechanism that shows
        main_model, main_view, main_controller = self.get_model_view_controller()

        main_view.context_cb.clear()

        contexts_root = (
            main_model.file_root
            / main_view.hemisphere_cb.currentText()
            / main_view.zone_cb.currentText()
            / main_view.easting_cb.currentText()
            / main_view.northing_cb.currentText()
        )
        res = main_controller.get_options(contexts_root)  
        res.sort(key=int)
        main_view.context_cb.addItems(res)

        main_view.context_cb.setCurrentIndex(0 if len(res) > 0 else -1)
        main_view.context_cb.setEnabled(len(res) > 1)

        main_controller.contextChanged()

    def contextChanged(self):
        main_model, main_view, main_controller = self.get_model_view_controller()

        main_view.statusLabel.setText(f"")
        main_view.selected_find.setText(f"")
        main_view.current_batch.setText(f"")
        main_view.current_piece.setText(f"")
        main_view.new_batch.setText(f"")
        main_view.new_piece.setText(f"")
        main_view.contextDisplay.setText(self.get_context_string())
        if hasattr(main_view, "current_pcd"):
            main_view.ply_window.remove_geometry(main_view.current_pcd)
            main_view.current_pcd = None

        model = QStandardItemModel(main_view)
        main_view.sorted_model_list.setModel(model)
        funcs_to_run = [
            ["Loading finds. It might take a while", main_controller.populate_finds],
            ["Loading models. It might take a while", main_controller.populate_models],
        ]

        now = time.time()
        main_controller.load_and_run(funcs_to_run)
        print(f"Timed passed: {time.time() - now} seconds")

    def get_context_string(self):
        """Return a string representing the full designation of the current context
        as utm_hemisphere-utm_zone-utm_easting-utm_northing-context_number

        Returns:
            str: The full designation of the currently selected context
        """
        main_model, main_view, main_controller = self.get_model_view_controller()

        hzenc = [
            main_view.hemisphere_cb.currentText(),
            main_view.zone_cb.currentText(),
            main_view.easting_cb.currentText(),
            main_view.northing_cb.currentText(),
            main_view.context_cb.currentText(),
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
        main_model, main_view, main_controller = self.get_model_view_controller()

        hemispheres = [
            d.name
            for d in main_model.file_root.iterdir()
            if d.name in main_model.path_variables["HEMISPHERES"] and d.is_dir()
        ]
 
        return hemispheres


    def get_options(self, path):
        res = [d.name for d in path.iterdir() if d.is_dir() and d.name.isdigit()]
        return res

