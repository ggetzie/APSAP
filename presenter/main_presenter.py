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
from presenter.mixins.filters.finds_and_objects_filter import FindsAndObjectsFilter

logger = logging.getLogger(__name__)


class MainPresenter(
    ChooseDirectoryMixin,
    MeasurePixelsDataMixin,
    Get3dModelSortedBySimilarityMixin,
    CalculateIndividualSimilaritiesMixin,
    LoadDataMixin,
    AddAndRemoveMatchMixin,
    FindsAndObjectsFilter,
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
        main_view.batch_start.valueChanged.connect(self.batch_start_change)
        main_view.batch_end.valueChanged.connect(self.batch_end_change)
        main_view.find_start.valueChanged.connect(self.find_start_change)
        main_view.find_end.valueChanged.connect(self.find_end_change)

        # Connecting the button to the function that load the images and 3d models
        main_view.loadAll.clicked.connect(self.load_images_plys)

        # Connecting the buttons that remove and update match to their handlers
        main_view.update_button.clicked.connect(self.add_match)
        main_view.remove_button.clicked.connect(self.remove_match)

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
        main_model, main_view, _ = self.get_model_view_presenter()
        main_view.hemisphere_cb.clear()

        options = main_model.hemisphere_list
        main_view.hemisphere_cb.addItems(options)
        # main_view.hemisphere_cb.setCurrentIndex(main_model.selected_hemisphere_idx)
        main_view.hemisphere_cb.setEnabled(len(options) > 1)
        self.populate_zones()

    def populate_zones(self):
        """Set the select options of zones as the zones under the current hemisphere"""
        main_model, main_view, _ = self.get_model_view_presenter()
        options = main_model.zone_list
        main_view.zone_cb.clear()
        main_view.zone_cb.addItems(options)
        # main_view.zone_cb.setCurrentIndex(main_model.selected_zone_idx)
        main_view.zone_cb.setEnabled(len(options) > 1)
        self.populate_eastings()

    def populate_eastings(self):
        """Set the select options of eastings as the eastings under the current zones"""
        main_model, main_view, _ = self.get_model_view_presenter()
        options = main_model.easting_list
        main_view.easting_cb.clear()
        main_view.easting_cb.addItems(options)
        # main_view.easting_cb.setCurrentIndex(main_model.selected_easting_idx)
        main_view.easting_cb.setEnabled(len(options) > 1)
        self.populate_northings()

    def populate_northings(self):
        """Set the select options of northings as the northings under the current eastings"""
        main_model, main_view, _ = self.get_model_view_presenter()
        options = main_model.northing_list
        main_view.northing_cb.clear()
        main_view.northing_cb.addItems(options)
        # main_view.northing_cb.setCurrentIndex(main_model.selected_northing_idx)
        main_view.northing_cb.setEnabled(len(options) > 1)
        self.populate_contexts()

    def populate_contexts(self):
        """Set the select options of contexts as the contexts under the current northing"""
        main_model, main_view, _ = self.get_model_view_presenter()
        options = [str(sc.context_number) for sc in main_model.context_list]
        main_view.context_cb.clear()
        main_view.context_cb.addItems(options)
        # main_view.context_cb.setCurrentIndex(main_model.selected_context_idx)
        main_view.context_cb.setEnabled(len(options) > 1)

    def populate_finds(self):
        main_model, main_view, _ = self.get_model_view_presenter()
        self.clear_selected_find()
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

    ##########################################################################
    #  onChange: Functions called in response to the user changing a select  #
    #  These functions update the main_model and repopulate the selects      #
    ##########################################################################

    def on_hemisphere_change(self):
        """This function is called when the user changes the hemisphere select"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        new_index = main_view.hemisphere_cb.currentIndex()
        if new_index != main_model.selected_hemisphere_idx:
            main_model.set_hemisphere_index(new_index)
            main_presenter.populate_zones()

    def on_zone_change(self):
        """This function is called when the user changes the zone select"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        new_index = main_view.zone_cb.currentIndex()
        if new_index != main_model.selected_zone_idx:
            main_model.set_zone_index(new_index)
            main_presenter.populate_eastings()

    def on_easting_change(self):
        """This function is called when the user changes the easting select"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        new_index = main_view.easting_cb.currentIndex()
        if new_index != main_model.selected_easting_idx:
            main_model.set_easting_index(new_index)
            main_presenter.populate_northings()

    def on_northing_change(self):
        """This function is called when the user changes the northing select"""
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        new_index = main_view.northing_cb.currentIndex()
        if new_index != main_model.selected_northing_idx:
            main_model.set_northing_index(new_index)
            main_presenter.populate_contexts()

    def on_context_change(self):
        """This function is called when the user changes the context select"""
        new_index = self.main_view.context_cb.currentIndex()
        if new_index != self.main_model.selected_context_idx:
            self.main_model.set_context_index(new_index)
            self.main_view.contextDisplay.setText(self.get_context_string())
            self.set_filter()

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

        main_model.set_selected_find_by_number(find_num)
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
        self.main_view.selected_find_info.setText("")
        self.main_view.selected_find.setText("")
        self.main_view.current_batch.setText("")
        self.main_view.current_year.setText("")
        self.main_view.current_piece.setText("")
