import logging
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
        main_presenter = self

        # Bind both the model and view into the presenter
        self.main_model: MainModel = MainModel()
        self.main_view: MainView = MainView()

        # Loading all the initial data of configuration
        self.main_model.prepare_data(self.main_view)

        self.set_up_view_presenter_connection()
        logger.info("Selected context: %s", self.main_model.selected_context)
        # Loading the first context
        self.populate_hemispheres()
        self.main_view.contextDisplay.setText(main_presenter.get_context_string())
        logger.info("Selected context: %s", self.main_model.selected_context)
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
        main_presenter = self

        # Connecting the selects of hemisphere, zone, easting, northing and context
        # with their handlers
        main_view.hemisphere_cb.currentIndexChanged.connect(
            main_presenter.on_hemisphere_change
        )
        main_view.zone_cb.currentIndexChanged.connect(main_presenter.on_zone_change)
        main_view.easting_cb.currentIndexChanged.connect(
            main_presenter.on_easting_change
        )
        main_view.northing_cb.currentIndexChanged.connect(
            main_presenter.on_northing_change
        )
        # main_view.context_cb.currentIndexChanged.connect(main_presenter.set_filter)
        main_view.context_cb.currentIndexChanged.connect(
            main_presenter.on_context_change
        )

        # Connecting the select list of of finds with its handler
        main_view.finds_list.currentItemChanged.connect(main_presenter.load_find_images)

        # Connecting the batch and find filters's four toggles to their handlers
        main_view.batch_start.valueChanged.connect(main_presenter.batch_start_change)
        main_view.batch_end.valueChanged.connect(main_presenter.batch_end_change)
        main_view.find_start.valueChanged.connect(main_presenter.find_start_change)
        main_view.find_end.valueChanged.connect(main_presenter.find_end_change)

        # Connecting the button to the function that load the images and 3d models
        main_view.loadAll.clicked.connect(main_presenter.load_images_plys)

        # Connecting the buttons that remove and update match to their handlers
        main_view.update_button.clicked.connect(main_presenter.add_match)
        main_view.remove_button.clicked.connect(main_presenter.remove_match)

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

    def populate_hemispheres(self):
        """Set the select options of hemisphere as the hemispheres in the root folder"""
        main_model, main_view, _ = self.get_model_view_presenter()
        main_view.hemisphere_cb.clear()

        options = main_model.hemisphere_list
        main_view.hemisphere_cb.addItems(options)
        main_view.hemisphere_cb.setCurrentIndex(main_model.selected_hemisphere_idx)
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
