import logging
import time

from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtGui import QColor

from model.main_model import MainModel
from view.main_view import MainView
from presenter.mixins.choose_directory.main_choose_directory import ChooseDirectoryMixin
from presenter.mixins.load_data.main_load_data import LoadDataMixin
from presenter.mixins.match.add_and_remove_match import AddAndRemoveMatchMixin

from presenter.mixins.calculate_similarity.get_3d_models_sorted_by_similarity import (
    Get3dModelSortedBySimilarityMixin,
)
from presenter.mixins.calculate_similarity.calculate_individual_similarities import (
    CalculateIndividualSimilaritiesMixin,
)

from presenter.mixins.measure_pixels_data.main_measure_pixels_data import (
    MeasurePixelsDataMixin,
)

logger = logging.getLogger(__name__)


class MainPresenter(
    ChooseDirectoryMixin,
    MeasurePixelsDataMixin,
    Get3dModelSortedBySimilarityMixin,
    CalculateIndividualSimilaritiesMixin,
    LoadDataMixin,
    AddAndRemoveMatchMixin,
):
    """This main_presenter inherits all the mixins' methods to handle the interactive
    behaviors of the applications, such that when you click on a button or choose an
    item in a select, things change in the application.
    """

    def __init__(self):

        # Bind both the model and view into the presenter
        now = time.time()
        logger.info("loading main model")
        self.main_model: MainModel = MainModel()
        logger.info("loaded main model in %s seconds", f"{time.time() - now:0.4f}")
        now = time.time()
        logger.info("loading main view")
        self.main_view: MainView = MainView()
        logger.info("loaded main view in %s seconds", f"{time.time() - now:0.4f}")

        # Loading all the initial data of configuration
        self.main_model.prepare_data(self.main_view)

        self.set_up_view_presenter_connection()

        # Loading the first context
        self.populate_hemispheres()
        self.main_view.contextDisplay.setText(str(self.main_model.selected_context))

        super().__init__()

    def get_model_view_presenter(self):

        return self.main_model, self.main_view, self

    def set_up_view_presenter_connection(self):
        """This function links the interaction from the user with the
        interface(main_view) via their handlers(main_presenter)

        Args:
            main_presenter (class): Containing all the functions that
            handle the interactions between the GUI and the Data

        """
        main_view = self.main_view

        # Connecting the selects of hemisphere, zone, easting, northing and context
        # with their handlers
        main_view.hemisphere_cb.currentIndexChanged.connect(self.on_hemisphere_change)
        main_view.zone_cb.currentIndexChanged.connect(self.on_zone_change)
        main_view.easting_cb.currentIndexChanged.connect(self.on_easting_change)
        main_view.northing_cb.currentIndexChanged.connect(self.on_northing_change)
        # main_view.context_cb.currentIndexChanged.connect(main_presenter.set_filter)
        main_view.context_cb.currentIndexChanged.connect(self.on_context_change)

        # Connecting the select list of of finds with its handler
        main_view.finds_list.currentItemChanged.connect(self.on_select_find)

        # Connecting the batch and find filters's four toggles to their handlers
        main_view.batch_start.valueChanged.connect(self.on_batch_start_change)
        main_view.batch_end.valueChanged.connect(self.on_batch_end_change)
        main_view.find_start.valueChanged.connect(self.on_find_start_change)
        main_view.find_end.valueChanged.connect(self.on_find_end_change)

        # Connecting the button to the function that load the images and 3d models
        main_view.loadAll.clicked.connect(self.on_load_all_clicked)

        # Connecting the buttons that remove and update match to their handlers
        main_view.update_button.clicked.connect(self.on_update_clicked)
        main_view.remove_button.clicked.connect(self.remove_match)

        main_view.initialize_unsorted_models()
        main_view.modelList.selectionModel().currentChanged.connect(
            self.change_3d_model
        )

        # Connect events for when the user selects a model
        # main_view.sorted_model_list.selectionModel().currentChanged.connect(
        #     main_presenter.change_3d_model
        # )

    def block_signals(self, boolean):
        """This function disables or enables all the interactive elements from the
        GUI when certain operations are being done at the moment

        Args:
            boolean (boolean): True means we disable interaction, False means we enable interaction
        """

        self.main_view.setDisabled(boolean)

    ##########################################################################
    #  Populate: Functions that populate the select options of the GUI       #
    #  Data is retrieved from the main_model and entered into the main_view  #
    ##########################################################################

    def populate_hemispheres(self):
        """Set the select options of hemisphere as the hemispheres in the root folder"""

        self.main_view.hemisphere_cb.clear()
        self.main_model.get_hemispheres()
        options = self.main_model.hemisphere_list
        self.main_view.hemisphere_cb.addItems(options)
        self.main_model.set_hemispheres_index(options.index("N"))
        # setting the index for the hemisphere selector will trigger
        # on_hemisphere_change, which will populate the zones and so on
        self.main_view.hemisphere_cb.setCurrentIndex(
            self.main_model.selected_hemisphere_idx
        )
        self.main_view.hemisphere_cb.setEnabled(len(options) > 1)

    def populate_zones(self):
        """Set the select options of zones as the zones under the current hemisphere"""
        self.main_model.get_zones()
        options = self.main_model.zone_list
        self.main_view.zone_cb.clear()
        self.main_view.zone_cb.addItems(options)
        self.main_view.zone_cb.setEnabled(len(options) > 1)

    def populate_eastings(self):
        """Set the select options of eastings as the eastings under the current zones"""
        self.main_model.get_eastings()
        options = self.main_model.easting_list
        self.main_view.easting_cb.clear()
        self.main_view.easting_cb.addItems(options)
        self.main_view.easting_cb.setEnabled(len(options) > 1)

    def populate_northings(self):
        """Set the select options of northings as the northings under the current eastings"""
        self.main_model.get_northings()
        options = self.main_model.northing_list
        self.main_view.northing_cb.clear()
        self.main_view.northing_cb.addItems(options)
        self.main_view.northing_cb.setEnabled(len(options) > 1)

    def populate_contexts(self):
        """Set the select options of contexts as the contexts under the current northing"""
        self.main_model.get_contexts()
        options = [str(sc.context_number) for sc in self.main_model.context_list]
        self.main_view.context_cb.clear()
        self.main_view.context_cb.addItems(options)
        # main_view.context_cb.setCurrentIndex(main_model.selected_context_idx)
        self.main_view.context_cb.setEnabled(len(options) > 1)

    def populate_finds(self):
        main_model, main_view = self.main_model, self.main_view
        self.clear_selected_find()
        main_view.clear_finds_list()

        self.block_signals(True)
        min_find = int(main_view.find_start.value())
        max_find = int(main_view.find_end.value())
        finds_list = [
            f
            for f in main_model.finds_list
            if (min_find <= f.find_number <= max_find) and f.has_photos()
        ]

        for find in finds_list:
            item = QListWidgetItem(str(find.find_number))
            if find.is_matched:
                item.setForeground(QColor("red"))
            main_view.finds_list.addItem(item)
        self.block_signals(False)

    ##########################################################################
    #  onChange: Functions called in response to the user changing a select  #
    #  These functions update the main_model and repopulate the selects      #
    ##########################################################################

    def on_hemisphere_change(self):
        """This function is called when the user changes the hemisphere select"""
        main_model, main_view = self.main_model, self.main_view
        new_index = main_view.hemisphere_cb.currentIndex()
        if new_index != main_model.selected_hemisphere_idx:
            main_model.set_hemispheres_index(new_index)
            self.populate_zones()

    def on_zone_change(self):
        """This function is called when the user changes the zone select"""
        main_model, main_view = self.main_model, self.main_view
        new_index = main_view.zone_cb.currentIndex()
        if new_index != main_model.selected_zone_idx:
            main_model.set_zone_index(new_index)
            self.populate_eastings()

    def on_easting_change(self):
        """This function is called when the user changes the easting select"""
        main_model, main_view = self.main_model, self.main_view
        new_index = main_view.easting_cb.currentIndex()
        if new_index != main_model.selected_easting_idx:
            main_model.set_easting_index(new_index)
            self.populate_northings()

    def on_northing_change(self):
        """This function is called when the user changes the northing select"""
        main_model, main_view = self.main_model, self.main_view
        new_index = main_view.northing_cb.currentIndex()
        if new_index != main_model.selected_northing_idx:
            main_model.set_northing_index(new_index)
            self.populate_contexts()

    def on_context_change(self):
        """This function is called when the user changes the context select"""
        main_model, main_view = self.main_model, self.main_view
        new_index = main_view.context_cb.currentIndex()
        if new_index != self.main_model.selected_context_idx:
            main_model.set_context_index(new_index)
            main_view.clear_interface()
            main_view.contextDisplay.setText(str(main_model.selected_context))
            self.set_filters()

    def on_select_find(self, selected_item):
        """This function would try to load the two images into the GUI and after finishing its operations,
        load the sorted 3d models.

        Args:
            selected_item (QListWidgetItem): The selected item in the finds_list
        """
        # Set the currently selected item

        # We test two things to see if we discard the subsequent operations of this function
        # 1. We check of the current selected item has text
        # 2. We check if the two supposedly existent pictures exist and are openable by the user
        # according to her access rights.
        main_view = self.main_view
        main_model = self.main_model
        logger.info("Selected item: %s type: %s", selected_item, type(selected_item))
        try:
            find_num = int(selected_item.text())
            logger.info("Selected find: %s", find_num)

        except AttributeError:
            main_view.clear_find_photos()
            return

        main_model.select_find(find_num)
        selected_find = main_model.selected_find
        main_view.selected_find_widget = selected_item.text()

        main_view.display_find_photo("front", selected_find.photo_path("front"))
        main_view.display_find_photo("back", selected_find.photo_path("back"))

        # Set up the selected_find's text
        main_view.selected_find.setText(str(find_num))

        if selected_find.is_matched:
            batch_year, batch_number, batch_piece = selected_find.get_match()
            main_view.current_year.setText(str(batch_year))
            main_view.current_batch.setText(str(batch_number))
            main_view.current_piece.setText(str(batch_piece))
        else:
            main_view.current_year.setText("NS")
            main_view.current_batch.setText("NS")
            main_view.current_piece.setText("NS")
            self.clean_ply_window()
        find_info = "\n".join(
            [
                f"Find: {find_num}",
                f"Material: {selected_find.material}",
                f"Category: {selected_find.category}",
            ]
        )
        main_view.selected_find_info.setText(f"\n{find_info}")

        # We immediately try to load all 3d models but sorted according to their
        # similarity with the current find
        self.load_sorted_models()

    def clear_selected_find(self):
        self.main_model.selected_find_number = None
        self.main_view.clear_find_info()

    def on_update_clicked(self):
        """This function is called when the user clicks on the update button"""
        selected_find = self.main_model.selected_find
        selected_a3dmodel = self.main_model.selected_a3dmodel

        if selected_find is None:
            self.main_view.display_error("Please select a find first")
            return
        if selected_a3dmodel is None:
            self.main_view.display_error("Please select a 3d model first")
            return

        message = (
            f"Update find ({selected_find}) to match 3d model ({selected_a3dmodel})?"
        )
        if selected_a3dmodel.is_matched:
            current_match = selected_a3dmodel.matched_finds[0]
            message += (
                f"\nModel {selected_a3dmodel} is already matched to find {current_match}"
                f"\nAfter this operation, find {current_match} will be unmatched"
            )

        self.main_view.confirm(message, self.on_update_confirmed)

    def on_update_confirmed(self, e):
        """This function tries to do two things when the ok button is clicked for add_match.
        First, it tries to update the database to reflect the matched result.
        Second, it tries to fix the added ceramic sherds and put them to the find folder.
        These sherds include the original-sized one and the

        Args:
            (button): The button that get clicked on.
        """
        main_model, main_view = self.main_model, self.main_view

        # In case that the button clicked is "OK"(e.g. Cancel), we don't do anything
        if not e.text() == "OK":
            logging.info("The user did not confirm the match: %s", e.text())
            return
        selected_find = main_model.selected_find
        old_a3dmodel = main_model.a3dmodels_dict.get(
            selected_find.get_match_str(), None
        )
        selected_a3dmodel = main_model.selected_a3dmodel
        old_find_number = None
        if selected_find is None or selected_a3dmodel is None:
            logging.error("No find or 3d model selected")
            return

        ##Updating the database
        if selected_a3dmodel.is_matched:
            old_find_number = selected_a3dmodel.matched_finds[0]
            success = main_model.clear_match_for_find(old_find_number)
            if not success:
                logging.error("Failed to clear match for find %s", old_find_number)

        success = main_model.match_selected_find_with_selected_a3dmodel()
        if not success:
            logging.error("There was an error updating the database")
            return

        # Create the folder in which we will put the 3d models (a subfolder in the find folder)
        models_dir = selected_find.models_directory()
        models_dir.mkdir(parents=True, exist_ok=True)

        mesh_path = selected_a3dmodel.get_file("mesh")
        orig_path = selected_a3dmodel.get_file("full")
        original_destination = models_dir / "a.ply"
        mesh_destination = models_dir / "a_0_3_mesh.ply"

        # We copy the files to the destination
        logging.info("Copying file from %s to %s", orig_path, original_destination)
        main_model.fix_and_copy_ply(str(orig_path), str(original_destination))
        logging.info("Copying file from %s to %s", mesh_path, mesh_destination)
        main_model.fix_and_copy_ply(str(mesh_path), str(mesh_destination))

        # We update the GUI to show that the find is matched to the 3d model
        main_view.set_find_color(selected_find.find_number, "red")
        if old_find_number is not None:
            main_view.set_find_color(old_find_number, "black")

        main_view.set_unsorted_model_color(
            selected_a3dmodel.batch_year,
            selected_a3dmodel.batch_number,
            selected_a3dmodel.batch_piece,
            "red",
        )

        main_view.set_sorted_model_color(
            str(selected_a3dmodel),
            "red",
        )
        if old_a3dmodel is not None:
            main_view.set_unsorted_model_color(
                old_a3dmodel.batch_year,
                old_a3dmodel.batch_number,
                old_a3dmodel.batch_piece,
                "black",
            )
            main_view.set_sorted_model_color(
                str(old_a3dmodel),
                "black",
            )

        # Update on the GUI that the find has the new matched 3d model
        new_year, new_batch, new_piece = str(selected_a3dmodel).split("-")
        main_view.current_year.setText(new_year)
        main_view.current_batch.setText(new_batch)
        main_view.current_piece.setText(new_piece)

    def set_filters(self):
        selected_context = self.main_model.selected_context
        if not selected_context:
            logger.warning("Tried setting filters without a selected context")
            return

        # set the find numbers filter
        find_numbers = [int(f) for f in selected_context.list_find_dirs()] or [0]
        self.main_view.find_start.setMinimum(min(find_numbers))
        self.main_view.find_start.setMaximum(max(find_numbers))
        self.main_view.find_start.setValue(min(find_numbers))
        self.main_view.find_end.setMinimum(min(find_numbers))
        self.main_view.find_end.setMaximum(max(find_numbers))
        self.main_view.find_end.setValue(max(find_numbers))

        # set the years filter. years will be an empty list if there are no batch folders
        years = selected_context.list_batch_years() or [0]
        self.main_view.year.setMinimum(min(years))
        self.main_view.year.setMaximum(max(years))
        if years != [0]:
            self.main_view.year.setValue(min(years))
        self.main_view.year.setReadOnly(years == [0])
        self.on_year_change()

    def on_year_change(self):
        selected_context = self.main_model.selected_context
        if not selected_context:
            logger.warning("Tried setting batch filters without a selected context")
            return
        year = self.main_view.year.value()
        batch_numbers = selected_context.list_batch_numbers(str(year)) or [0]
        self.main_view.batch_start.setMinimum(min(batch_numbers))
        self.main_view.batch_start.setMaximum(max(batch_numbers))
        self.main_view.batch_start.setValue(min(batch_numbers))
        self.main_view.batch_end.setMinimum(min(batch_numbers))
        self.main_view.batch_end.setMaximum(max(batch_numbers))
        self.main_view.batch_end.setValue(max(batch_numbers))

    def on_batch_start_change(self):
        self.main_view.batch_end.setMinimum(self.main_view.batch_start.value())

    def on_batch_end_change(self):
        self.main_view.batch_start.setMaximum(self.main_view.batch_end.value())

    def on_find_start_change(self):
        self.main_view.find_end.setMinimum(self.main_view.find_start.value())

    def on_find_end_change(self):
        self.main_view.find_start.setMaximum(self.main_view.find_end.value())

    def on_load_all_clicked(self):
        selected_context = self.main_model.selected_context
        if not selected_context:
            logger.error("Tried to load finds and models without context selected")
            return
        self.main_model.load_finds()
        self.main_model.load_a3dmodels()
        self.populate_finds()
        self.populate_models()
