import time
from PyQt5.QtGui import (
    QStandardItemModel,
)

from PyQt5.QtWidgets import QMainWindow, QSplashScreen

##potential view
class LoadingSplash(QSplashScreen):
    def mousePressEvent(self, event):

        pass


class SelectPathMixin: 

    def populate_hemispheres(self):

        # Getting m, v, c from to update the gui and get the data.
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        # Clear the combox box
        main_view.hemisphere_cb.clear()

        # Get the hemispheres and add it to the combo box
        options = main_presenter.get_hemispheres()
        main_view.hemisphere_cb.addItems(options)
        # Set the index of the select as 0 by default and allow the select to be "selected"  if there are more than 1 elements
        main_view.hemisphere_cb.setCurrentIndex(0 if len(options) > 0 else -1)
        main_view.hemisphere_cb.setEnabled(len(options) > 1)


    def populate_zones(self):
        # Check populate_zones for explanations
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        if main_view.hemisphere_cb.count() > 0 :
            
            main_view.zone_cb.clear()

            hemisphere = main_view.hemisphere_cb.currentText()
            zone_root = main_model.file_root / hemisphere
            options = main_presenter.get_options(zone_root)
            main_view.zone_cb.addItems(options)

            main_view.zone_cb.setCurrentIndex(0 if len(options) > 0 else -1)
            main_view.zone_cb.setEnabled(len(options) > 1)

    def populate_eastings(self):
        # Check populate_zones for explanations
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
        # Check populate_zones for explanations
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        #Make sure that we only populate if the current items if the previous items
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
        # Check populate_zones for explanations,  except this "populate" function takes the final functions populate_finds and populate_models in a load_and_run mechanism that shows


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
            


    def contextChanged(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        if main_view.context_cb.count() > 0:

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
                ["Loading finds. It might take a while", main_presenter.populate_finds],
                ["Loading models. It might take a while", main_presenter.populate_models],
            ]

            now = time.time()
            main_presenter.load_and_run(funcs_to_run)
            print(f"Time for loading plys and models passed: {time.time() - now} seconds")

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

    def load_and_run(self, funcs_to_run):
        # Load the splash
        splash = LoadingSplash()
        splash.show()
        # Run all functions and the message during loading time
        for message_func in funcs_to_run:
            message = message_func[0]
            func = message_func[1]
            splash.showMessage(message)
            func()
        # Close the window
        window = QMainWindow()
        window.show()
        splash.finish(window)

    def get_hemispheres(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        hemispheres = [
            d.name
            for d in main_model.file_root.iterdir()
            if d.name in main_model.path_variables["HEMISPHERES"] and d.is_dir()
        ]

        return hemispheres

    def get_options(self, path):
        options = [d.name for d in path.iterdir() if d.is_dir() and d.name.isdigit()]
        return options
