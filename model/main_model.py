# In MVVM, Model View ViewModel architecture, Model represents the data in the application.

import pathlib
from typing import List
from model.mixins.file_IO import FileIOMixin
from model.mixins.database import DatabaseMixin
from model.mixins.initial_load import InitialLoadMixin
from model.mixins.copy_file import CopyFileMixin
from model.constants import BASE_DATA_DIR
from model.models import SpatialContext


class MainModel(InitialLoadMixin, FileIOMixin, DatabaseMixin, CopyFileMixin):
    """The MainModel contains data-related libraries and functions, imported from various mixins.

    Args:
        InitialLoadMixin (class): This mixin contains the function prepare_data()
        along with other functions to help with the initial loading of the whole application
        FileIOMixin (class): This mixin contains the functions related to opening JSON
        and Image files
        DatabaseMixin (class): This mixin contains the functions related to get and
        update the ceramic find information from the database
        CopyFileMixin (class): This mixin contains the function fix_and_copy_ply() that
        opens a 3d model, fixes it, then save it to another place.
    """

    def __init__(self):
        super().__init__()
        self.hemisphere_list: List[str] = [
            d.name
            for d in BASE_DATA_DIR.iterdir()
            if d.is_dir() and d.name in ["N", "S"]
        ]
        self.selected_hemisphere_idx: int = self.hemisphere_list.index("N")
        hemisphere_dir: pathlib.Path = (
            BASE_DATA_DIR / self.hemisphere_list[self.selected_hemisphere_idx]
        )
        self.zone_list: List[str] = [
            d.name
            for d in hemisphere_dir.iterdir()
            if d.is_dir() and d.name.isnumeric()
        ]
        self.selected_zone_idx: int = 0
        zone_dir: pathlib.Path = hemisphere_dir / self.zone_list[self.selected_zone_idx]
        self.easting_list: List[str] = [
            d.name for d in zone_dir.iterdir() if d.is_dir() and d.name.isnumeric()
        ]
        self.selected_easting_idx: int = 0
        easting_dir: pathlib.Path = (
            zone_dir / self.easting_list[self.selected_easting_idx]
        )
        self.northing_list: List[str] = [
            d.name for d in easting_dir.iterdir() if d.is_dir() and d.name.isnumeric()
        ]
        self.selected_northing_idx: int = 0
        northing_dir: pathlib.Path = (
            easting_dir / self.northing_list[self.selected_northing_idx]
        )
        self.context_list: List[SpatialContext] = [
            SpatialContext(
                utm_hemisphere=self.hemisphere_list[self.selected_hemisphere_idx],
                utm_zone=int(self.zone_list[self.selected_zone_idx]),
                area_utm_easting_meters=int(
                    self.easting_list[self.selected_easting_idx]
                ),
                area_utm_northing_meters=int(
                    self.northing_list[self.selected_northing_idx]
                ),
                context_number=int(d.name),
            )
            for d in northing_dir.iterdir()
            if d.is_dir() and d.name.isnumeric()
        ]
        self.selected_context_idx: int = 0
        self._finds_list = []
        self._selected_find_idx = None

    def set_finds_list(self):
        sc = self.context_list[self.selected_context_idx]
        self._finds_list = sc.list_finds(self.conn.cursor())
        self._selected_find_idx = 0

    def select_find(self, idx):
        self._selected_find_idx = idx

    @property
    def selected_find(self):
        if self._selected_find_idx is None:
            return None
        return self._finds_list[self._selected_find_idx]
