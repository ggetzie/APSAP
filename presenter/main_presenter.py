import time
import logging
import re
from pathlib import PurePath

from PyQt5.QtGui import QFont

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

    def __init__(self, model, view):
        main_presenter = self

        # Bind both the model and view into the presenter
        self.main_model = model
        self.main_view = view

        # Loading all the initial data of configuration
        self.main_model.prepare_data(self.main_view)

        # Setting up the connections between the presenters' methods and
        # the buttons, selects and other gui elements in the view
        self.main_view.set_up_view_presenter_connection(main_presenter)

        # Loading the first context
        self.populate_hemispheres()
        view.contextDisplay.setText(main_presenter.get_context_string())

        super().__init__()

    def get_model_view_presenter(self):

        return self.main_model, self.main_view, self

    def block_signals(self, boolean):
        """This function disables or enables all the interactive elements from the
        GUI when certain operations are being done at the moment

        Args:
            boolean (boolean): True means we disable interaction, False means we enable interaction
        """
        _, main_view, _ = self.get_model_view_presenter()

        main_view.setDisabled(boolean)
        # main_view.hemisphere_cb.setDisabled(boolean)
        # main_view.zone_cb.setDisabled(boolean)
        # main_view.easting_cb.setDisabled(boolean)
        # main_view.northing_cb.setDisabled(boolean)
        # main_view.context_cb.setDisabled(boolean)

        # main_view.finds_list.setDisabled(boolean)

        # main_view.batch_start.setDisabled(boolean)
        # main_view.batch_end.setDisabled(boolean)
        # main_view.find_start.setDisabled(boolean)
        # main_view.find_end.setDisabled(boolean)

        # main_view.loadAll.setDisabled(boolean)

        # main_view.update_button.setDisabled(boolean)
        # main_view.remove_button.setDisabled(boolean)

        # main_view.modelList.setDisabled(boolean)
        # main_view.sorted_model_list.setDisabled(boolean)

        # main_view.year.setDisabled(boolean)

        # if boolean == True:
        #     logging.info("GUI disabled")
        # else:
        #     logging.info("GUI enabled")
