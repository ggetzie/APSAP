import ctypes

# opengl_path = r".\computation\opengl32.dll"
# ctypes.cdll.LoadLibrary(opengl_path)

from view.mixins.ply_window import PlyWindowMixin
from view.mixins.image_window import OpenImageMixin
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic


class MainView(QMainWindow, PlyWindowMixin, OpenImageMixin):
    """The MainView contains all the GUI related functions and classes

    Args:
        QMainWindow (QMainWindow): Making the MainView a QWidget that can load a
        ui file and display things.

        PlyWindowMixin (class): Mixin that initializes the window that displays 3d models in it.

        OpenImageMixin (class): Mixin that allows the users to click on an
        Image to see it full size.
    """

    def __init__(self):
        """This constructor loads the ply to the ui file, set up the 3d model window,
        and make it the images pop when you click on them.
        """
        super(MainView, self).__init__()
        uic.loadUi("view/ui_files/MainWindow.ui", self)

        self.set_up_ply_window()
        self.set_up_images_pop_up()

    def set_up_view_presenter_connection(self, main_presenter):
        """This function links the interaction from the user with the
        interface(main_view) via their handlers(main_presenter)

        Args:
            main_presenter (class): Containing all the functions that
            handle the interactions between the GUI and the Data

        """
        main_view = self

        # Connecting the selects of hemisphere, zone, easting, northing and context
        # with their handlers
        main_view.hemisphere_cb.currentIndexChanged.connect(
            main_presenter.populate_zones
        )
        main_view.zone_cb.currentIndexChanged.connect(main_presenter.populate_eastings)
        main_view.easting_cb.currentIndexChanged.connect(
            main_presenter.populate_northings
        )
        main_view.northing_cb.currentIndexChanged.connect(
            main_presenter.populate_contexts
        )
        main_view.context_cb.currentIndexChanged.connect(main_presenter.set_filter)

        # Connecting the select list of of finds with its handler
        main_view.finds_list.currentItemChanged.connect(main_presenter.load_find_images)

        # Connecting the batch and find filters's four toggles to their handlers
        main_view.batch_start.valueChanged.connect(main_presenter.batch_start_change)
        main_view.batch_end.valueChanged.connect(main_presenter.batch_end_change)
        main_view.find_start.valueChanged.connect(main_presenter.find_start_change)
        main_view.find_end.valueChanged.connect(main_presenter.find_end_change)

        # Connecting the button to the function that load the images and 3d models
        main_view.loadAll.clicked.connect(main_presenter.loadImagesPlys)

        # Connecting the buttons that remove and update match to their handlers
        main_view.update_button.clicked.connect(main_presenter.add_match)
        main_view.remove_button.clicked.connect(main_presenter.remove_match)
