import logging
import time
from typing import List, Tuple

from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QColor, QStandardItem

from model.main_model import MainModel
from model.models import A3DModel, ObjectFind
from model.workers.test import TestWorker
from model.workers.fix_move_ply_worker import FixMovePlyWorker

# from model.models import year_batch_piece_str
from view.main_view import MainView

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
    MeasurePixelsDataMixin,
    Get3dModelSortedBySimilarityMixin,
    CalculateIndividualSimilaritiesMixin,
):
    """This main_presenter inherits all the mixins' methods to handle the interactive
    behaviors of the applications, such that when you click on a button or choose an
    item in a select, things change in the application.
    """

    def __init__(self, debug: bool = False):

        # Bind both the model and view into the presenter
        self.debug = debug
        self.threadpool = QThreadPool()
        now = time.time()
        logger.info("loading main model")
        self.main_model: MainModel = MainModel(skip_ply=True)
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
        self.main_view.context_display.setText(str(self.main_model.selected_context))

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
        main_view.context_cb.currentIndexChanged.connect(self.on_context_change)

        # Connecting the select list of of finds with its handler
        main_view.finds_list.currentItemChanged.connect(self.on_select_find)

        # Connecting the batch and find filters's four toggles to their handlers
        main_view.batch_start.valueChanged.connect(self.on_batch_start_change)
        main_view.batch_end.valueChanged.connect(self.on_batch_end_change)
        main_view.find_start.valueChanged.connect(self.on_find_start_change)
        main_view.find_end.valueChanged.connect(self.on_find_end_change)

        # Connecting the button to the function that load the images and 3d models
        main_view.load_all.clicked.connect(self.on_load_all_clicked)

        # Connecting the buttons that remove and update match to their handlers
        main_view.update_button.clicked.connect(self.on_update_clicked)
        main_view.unmatch_find_button.clicked.connect(self.on_unmatch_find_clicked)
        main_view.unmatch_model_button.clicked.connect(self.on_unmatch_model_clicked)

        main_view.unsorted_model_list.selectionModel().currentChanged.connect(
            self.on_select_model
        )
        main_view.sorted_model_list.selectionModel().currentChanged.connect(
            self.on_select_model
        )

        # testing background tasks
        # main_view.test_task_button.clicked.connect(self.on_test_clicked)

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
        self.clear_selected_find()
        self.main_view.clear_finds_list()
        min_find = int(self.main_view.find_start.value())
        max_find = int(self.main_view.find_end.value())
        finds_list = self.main_model.list_finds(min_find=min_find, max_find=max_find)
        self.main_view.list_finds(finds_list)

    def populate_unsorted_models(self):
        # TODO move this to the view. Pass in a list of models and
        # have the view sort and group them by year, batch, piece
        # as it places them in the unsorted models widget
        self.main_view.clear_unsorted_models()
        self.block_signals(True)
        nested_a3dmodels = self.main_model.get_nested_a3dmodels()
        filter_year = self.main_view.year.value()
        min_batch = self.main_view.batch_start.value()
        max_batch = self.main_view.batch_end.value()
        for batch_year in sorted(nested_a3dmodels.keys()):
            if batch_year != int(filter_year):
                continue
            year_item = QStandardItem(f"{batch_year}")
            for batch_number in sorted(nested_a3dmodels[batch_year].keys()):
                if int(batch_number) < int(min_batch) or int(batch_number) > int(
                    max_batch
                ):
                    continue
                batch_item = QStandardItem(f"{batch_number}")
                for piece_number in sorted(
                    nested_a3dmodels[batch_year][batch_number].keys()
                ):
                    a3dmodel = nested_a3dmodels[batch_year][batch_number][piece_number]
                    # logger.debug("Measuring pixels for %s", a3dmodel)
                    # self.measure_pixels_3d(a3dmodel)
                    model_piece = QStandardItem(f"{piece_number}")
                    model_piece.setData(str(a3dmodel), Qt.UserRole)
                    if a3dmodel.is_matched:
                        model_piece.setForeground(QColor("red"))
                    batch_item.appendRow(model_piece)
                year_item.appendRow(batch_item)
            self.main_view.unsorted_model_list.selectionModel().model().appendRow(
                year_item
            )
        self.block_signals(False)

    def populate_sorted_models(self):

        selected_find = self.main_model.selected_find
        # if not selected_find.is_measured:
        #     self.main_view.display_error(
        #         "Couldn't measure this find. Models are not sorted by similarity"
        #     )
        #     models_sorted_by_similarity = self.main_model.a3dmodels_list
        # else:
        #     # models_sorted_by_similarity: List[A3DModel] = (
        #     #     self.main_model.list_a3dmodels_by_similarity(
        #     #         self.main_model.selected_find.find_number
        #     #     )
        #     # )
        models_sorted_by_similarity: List[A3DModel] = (
            self.get_potential_3d_models_sorted_by_similarity(selected_find)
        )
        self.main_view.clear_sorted_models()
        self.main_view.clear_ply_window()
        self.block_signals(True)
        filter_year = self.main_view.year.value()
        min_batch = self.main_view.batch_start.value()
        max_batch = self.main_view.batch_end.value()
        filtered_models = [
            m
            for m in models_sorted_by_similarity
            if (m.batch_year == int(filter_year))
            and (m.batch_number >= int(min_batch))
            and (m.batch_number <= int(max_batch))
        ]

        self.main_view.list_sorted_models(filtered_models)
        self.main_view.sorted_model_list.selectionModel().currentChanged.connect(
            self.on_select_model
        )

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
            main_view.context_display.setText(str(main_model.selected_context))
            self.set_filters()

    def on_select_find(self, selected_item):
        """This function would try to load the two images into the GUI and after finishing its
        operations, load the sorted 3d models.

        Args:
            selected_item (QListWidgetItem): The selected item in the finds_list
        """
        # Set the currently selected item
        logger.debug("Selected item: %s type: %s", selected_item, type(selected_item))
        try:
            find_num = int(selected_item.text())
            logger.debug("Selected find: %s", find_num)

        except AttributeError:
            self.main_view.clear_find_photos()
            logger.error(
                "Could not get find number from selected item %s", selected_item
            )
            return

        self.main_model.select_find(find_num)
        self.main_view.display_find_details(self.main_model.selected_find)
        self.main_view.display_model_details(None)  # clear the model details

        # We immediately try to load all 3d models but sorted according to their
        # similarity with the current find
        self.populate_sorted_models()

    def on_select_model(self, selected_item):
        ply_str = selected_item.data(Qt.UserRole)
        self.main_model.select_a3dmodel(ply_str)
        a3dmodel = self.main_model.selected_a3dmodel
        if a3dmodel is None:
            logger.warning("The 3d model %s is not found", ply_str)
            return
        self.main_view.display_model_details(a3dmodel)

    def clear_selected_find(self):
        self.main_model.selected_find_number = None
        self.main_view.clear_find_info()

    ##########################################################################
    #  on_clicked: Functions called in response to the user clicking a       #
    #  button.                                                               #
    ##########################################################################

    def on_load_all_clicked(self):
        selected_context = self.main_model.selected_context
        if not selected_context:
            self.main_view.display_error("Please select a context first")
            logger.error("Tried to load finds and models without context selected")
            return

        # self.main_view.general_status.setText("Measuring finds in background")
        _ = self.main_model.load_finds(color_grid=self.main_view.current_color_grid())

        # w.signals.progress.connect(self.on_task_progress)
        # w.signals.finished.connect(self.on_measure_finds_finished)
        # w.signals.error.connect(self.on_task_error)
        # self.threadpool.start(w)
        self.main_model.load_a3dmodels()
        self.populate_finds()
        self.populate_unsorted_models()

    def on_update_clicked(self):
        """This function is called when the user clicks on the update button.
        In order to update a match, a find must be selected and a 3d model must be selected.
        The selected find and model must also not be matched to anything else.
        """
        selected_find = self.main_model.selected_find
        selected_a3dmodel = self.main_model.selected_a3dmodel

        if selected_find is None:
            self.main_view.display_error("Please select a find first")
            return
        if selected_a3dmodel is None:
            self.main_view.display_error("Please select a 3d model first")
            return

        if selected_a3dmodel.is_matched:
            msg = (
                f"Model {selected_a3dmodel} is already matched to a find\n"
                "Make sure model and find are unmatched before updating."
            )
            self.main_view.display_error(msg)
            return

        if selected_find.is_matched:
            msg = (
                f"Find {selected_find} is already matched to a model\n"
                "Make sure model and find are unmatched before updating."
            )
            self.main_view.display_error(msg)
            return
        message = (
            f"Update find ({selected_find}) to match 3d model ({selected_a3dmodel})?"
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
        # In case that the button clicked is "OK"(e.g. Cancel), we don't do anything
        if not e.text() == "OK":
            logger.debug("The user did not confirm the match: %s", e.text())
            return
        selected_find = self.main_model.selected_find
        selected_a3dmodel = self.main_model.selected_a3dmodel
        if selected_find is None or selected_a3dmodel is None:
            logger.error("No find or 3d model selected")
            return
        # check again that model and find are not already matched
        if selected_find.is_matched or selected_a3dmodel.is_matched:
            logger.error("Find or model already matched")
            self.main_view.display_error(
                "Find or model already matched.\nMake sure they are unmatched before updating."
            )
            return

        success = self.main_model.match_selected_find_with_selected_a3dmodel()
        if not success:
            logger.error("There was an error updating the database")
            return

        # Create the folder in which we will put the 3d models (a subfolder in the find folder)
        models_dir = selected_find.models_directory()
        models_dir.mkdir(parents=True, exist_ok=True)

        mesh_path = selected_a3dmodel.get_file("mesh")
        orig_path = selected_a3dmodel.get_file("full")
        original_destination = models_dir / "a.ply"
        mesh_destination = models_dir / "a_0_3_mesh.ply"
        pairs = [(orig_path, original_destination), (mesh_path, mesh_destination)]

        # Copy the files in the background
        worker = FixMovePlyWorker(
            pairs, str(selected_a3dmodel), selected_find.find_number
        )
        worker.signals.progress.connect(self.on_task_progress)
        worker.signals.finished.connect(self.on_task_finished)
        worker.signals.error.connect(self.on_task_error)
        self.threadpool.start(worker)

        # Update on the GUI that the find has the new matched 3d model
        self.main_view.update_find_match_info(selected_find)
        self.main_view.update_model_match_info(selected_a3dmodel)

    def on_unmatch_find_clicked(self):
        """This function is called when the user clicks on the unmatch find button.
        Confirm that they really want to unmatch the find"""
        selected_find = self.main_model.selected_find

        if selected_find is None:
            self.main_view.display_error("Please select a find first")
            return

        message = f"Unmatch find ({selected_find}) from 3d model ({selected_find.get_match_str()})?"

        self.main_view.confirm(message, self.on_unmatch_find_confirmed)

    def on_unmatch_find_confirmed(self, e):
        if not e.text() == "OK":
            logger.debug("The user did not confirm the match: %s", e.text())
            return
        selected_find = self.main_model.selected_find
        if not selected_find:
            logger.error("No find selected")
            return
        old_match: A3DModel = self.main_model.a3dmodels_dict[
            selected_find.get_match_str()
        ]
        # remove the match in the model, updating the database
        self.main_model.clear_match_for_find(selected_find.find_number)

        # update the GUI
        self.main_view.set_find_color(selected_find.find_number, "black")
        self.main_view.set_unsorted_model_color(
            old_match.batch_year,
            old_match.batch_number,
            old_match.batch_piece,
            "black",
        )
        self.main_view.set_sorted_model_color(str(old_match), "black")
        self.main_view.update_find_match_info(selected_find)
        self.main_view.update_model_match_info(self.main_model.selected_a3dmodel)

    def on_unmatch_model_clicked(self):
        """This function is called when the user clicks on the unmatch model button.
        Confirm that they really want to unmatch the model"""
        selected_a3dmodel = self.main_model.selected_a3dmodel

        if selected_a3dmodel is None:
            self.main_view.display_error("Please select a 3d model first")
            return
        plural = "s" if len(selected_a3dmodel.matched_finds) > 1 else ""
        find_nums = ",".join(str(f) for f in selected_a3dmodel.matched_finds)
        message = (
            f"Unmatch 3d model ({selected_a3dmodel}) from find{plural} ({find_nums})?"
        )

        self.main_view.confirm(message, self.on_unmatch_model_confirmed)

    def on_unmatch_model_confirmed(self, e):
        if not e.text() == "OK":
            logger.debug("The user did not confirm the match: %s", e.text())
            return
        selected_a3dmodel = self.main_model.selected_a3dmodel
        if not selected_a3dmodel:
            logger.error("No 3d model selected")
            return
        matched_finds: List[ObjectFind] = [
            self.main_model.finds_dict[f] for f in selected_a3dmodel.matched_finds
        ]
        for find in matched_finds:
            self.main_model.clear_match_for_find(find.find_number)
            self.main_view.set_find_color(find.find_number, "black")

        # update the GUI
        self.main_view.set_unsorted_model_color(
            selected_a3dmodel.batch_year,
            selected_a3dmodel.batch_number,
            selected_a3dmodel.batch_piece,
            "black",
        )
        self.main_view.set_sorted_model_color(str(selected_a3dmodel), "black")
        self.main_view.update_model_match_info(selected_a3dmodel)
        self.main_view.update_find_match_info(self.main_model.selected_find)

    # testing background tasks
    def on_test_clicked(self):
        worker = TestWorker()
        worker.signals.progress.connect(self.on_task_progress)
        worker.signals.finished.connect(self.on_task_finished)
        self.threadpool.start(worker)

    def set_filters(self):
        selected_context = self.main_model.selected_context
        if not selected_context:
            logger.warning("Tried setting filters without a selected context")
            return
        find_numbers = [int(f) for f in selected_context.list_find_dirs()] or [0]
        years = selected_context.list_batch_years() or [0]
        self.main_view.set_find_year_filters(
            min(years), max(years), min(find_numbers), max(find_numbers)
        )
        self.on_year_change()

    def on_year_change(self):
        selected_context = self.main_model.selected_context
        if not selected_context:
            logger.warning("Tried setting batch filters without a selected context")
            return
        year = self.main_view.year.value()
        batch_numbers = selected_context.list_batch_numbers(str(year)) or [0]
        self.main_view.set_batch_filters(min(batch_numbers), max(batch_numbers))

    def on_batch_start_change(self):
        self.main_view.batch_end.setMinimum(self.main_view.batch_start.value())

    def on_batch_end_change(self):
        self.main_view.batch_start.setMaximum(self.main_view.batch_end.value())

    def on_find_start_change(self):
        self.main_view.find_end.setMinimum(self.main_view.find_start.value())

    def on_find_end_change(self):
        self.main_view.find_start.setMaximum(self.main_view.find_end.value())

    ##########################################################################
    #  on_task: Functions called in response to the background tasks         #
    #  These functions update the progress bar and display messages          #
    ##########################################################################

    def on_task_progress(self, progress: Tuple[str, int]):
        self.main_view.display_progress(progress)

    def on_task_finished(self, message: str):
        self.main_view.display_progress((message, 0))

    def on_measure_finds_finished(self, message: str):
        self.main_view.display_progress((message, 0))
        self.main_view.general_status.setText("")

    def on_task_error(self, message: str):
        self.main_view.display_progress((message, 0))
