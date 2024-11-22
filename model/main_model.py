# In MVP, Model View Presenter architecture, Model represents the data in the application.
import logging
from operator import attrgetter
from typing import List, Dict
from model.mixins.file_IO import FileIOMixin
from model.mixins.database import DatabaseMixin
from model.mixins.initial_load import InitialLoadMixin
from model.mixins.copy_file import CopyFileMixin
from model.constants import BASE_DATA_DIR
from model.models import (
    SpatialContext,
    A3DModel,
    ObjectFind,
)

logger = logging.getLogger(__name__)


# initial_context="N-38-478130-4419430-109"
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

        self.finds_dict: Dict[int:ObjectFind] = {}  # find_number: int -> ObjectFind
        self.selected_find_number: int = None

        self.a3dmodels_dict: Dict[str:A3DModel] = {}  # a3dmodel_str: str -> A3DModel
        self.selected_a3dmodel_str: str = None  # identify by year-batch-piece

        self.context_list: List[SpatialContext] = []
        self.selected_context_idx: int = None
        self.northing_list: List[str] = []
        self.selected_northing_idx: int = None
        self.easting_list: List[str] = []
        self.selected_easting_idx: int = None
        self.zone_list: List[str] = []
        self.selected_zone_idx = None

        ## calling set_hemispheres_index() will cascade through zone/easting/northing/context
        ## to get the available options and set default index to 0 for each
        self.hemisphere_list: List[str] = self.get_hemispheres()
        self.selected_hemisphere_idx = 0
        self.set_hemispheres_index(self.hemisphere_list.index("N"))

    def select_find(self, find_number: int):
        self.selected_find_number = find_number

    @property
    def selected_find(self) -> ObjectFind:
        return self.finds_dict.get(self.selected_find_number, None)

    def select_a3dmodel(self, a3dmodel_str: str):
        self.selected_a3dmodel_str = a3dmodel_str

    @property
    def selected_a3dmodel(self) -> A3DModel:
        return self.a3dmodels_dict.get(self.selected_a3dmodel_str, None)

    @property
    def selected_context(self) -> SpatialContext:
        if self.selected_context_idx is None:
            return None
        return self.context_list[self.selected_context_idx]

    @property
    def finds_list(self) -> List[ObjectFind]:
        return sorted(self.finds_dict.values(), key=attrgetter("find_number"))

    @property
    def a3dmodels_list(self) -> List[A3DModel]:
        return sorted(
            self.a3dmodels_dict.values(),
            key=attrgetter("batch_year", "batch_number", "batch_piece"),
        )

    def get_hemispheres(self) -> List[str]:
        return [
            d.name
            for d in BASE_DATA_DIR.iterdir()
            if d.is_dir() and d.name in ["N", "S"]
        ]

    def set_hemispheres_index(self, idx):
        logger.info("Setting hemisphere index to %s", idx)
        self.selected_hemisphere_idx = idx
        self.zone_list = self.get_zones(
            self.hemisphere_list[self.selected_hemisphere_idx]
        )
        self.set_zone_index(0)

    def get_zones(self, hemisphere) -> List[str]:
        hemisphere_dir = BASE_DATA_DIR / hemisphere
        return [
            d.name
            for d in hemisphere_dir.iterdir()
            if d.is_dir() and d.name.isnumeric()
        ]

    def set_zone_index(self, idx):
        logger.info("Setting zone index to %s", idx)
        self.selected_zone_idx = idx
        self.easting_list = self.get_eastings(
            self.hemisphere_list[self.selected_hemisphere_idx],
            self.zone_list[self.selected_zone_idx],
        )
        self.set_easting_index(0)

    def get_eastings(self, hemisphere, zone) -> List[str]:
        zone_dir = BASE_DATA_DIR / hemisphere / zone
        return [d.name for d in zone_dir.iterdir() if d.is_dir() and d.name.isnumeric()]

    def set_easting_index(self, idx):
        logger.info("Setting easting index to %s", idx)
        self.selected_easting_idx = idx
        self.northing_list = self.get_northings(
            self.hemisphere_list[self.selected_hemisphere_idx],
            self.zone_list[self.selected_zone_idx],
            self.easting_list[self.selected_easting_idx],
        )
        self.set_northing_index(0)

    def get_northings(self, hemisphere, zone, easting) -> List[str]:
        easting_dir = BASE_DATA_DIR / hemisphere / zone / easting
        return [
            d.name for d in easting_dir.iterdir() if d.is_dir() and d.name.isnumeric()
        ]

    def set_northing_index(self, idx):
        logger.info("Setting northing index to %s", idx)
        self.selected_northing_idx = idx
        self.context_list = [
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
            for d in (
                BASE_DATA_DIR
                / self.hemisphere_list[self.selected_hemisphere_idx]
                / self.zone_list[self.selected_zone_idx]
                / self.easting_list[self.selected_easting_idx]
                / self.northing_list[self.selected_northing_idx]
            ).iterdir()
            if d.is_dir() and d.name.isnumeric()
        ]
        self.context_list.sort(key=attrgetter("context_number"))
        self.set_context_index(0)

    def set_context_index(self, idx):
        self.selected_context_idx = idx
        self.finds_dict = {
            f.find_number: f
            for f in self.selected_context.list_finds(self.conn.cursor())
        }
        self.selected_find_number = (
            list(self.finds_dict.keys())[0] if self.finds_dict else None
        )

        self.a3dmodels_dict = {str(m): m for m in self.selected_context.list_models()}

        self.selected_a3dmodel_str = (
            list(self.a3dmodels_dict.keys())[0] if self.a3dmodels_dict else None
        )
        for a3dmodel in self.a3dmodels_list:
            a3dmodel.matched_finds = a3dmodel.get_matches(self.conn.cursor())

    def get_nested_a3dmodels(self):
        by_year = {}
        for model in self.a3dmodels_list:
            if model.batch_year not in by_year:
                by_year[model.batch_year] = {}
            if model.batch_number not in by_year[model.batch_year]:
                by_year[model.batch_year][model.batch_number] = {}
            by_year[model.batch_year][model.batch_number][model.batch_piece] = model
        return by_year

    def clear_match_for_find(self, find_number: int) -> bool:
        find = self.finds_dict.get(find_number, None)
        if find is None:
            return False
        old_match = self.a3dmodels_dict[find.get_match_str()]
        if old_match is None:
            return False
        find.clear_match(self.conn.cursor())
        old_match.matched_finds = old_match.get_matches(self.conn.cursor())
        return True

    def match_selected_find_with_selected_a3dmodel(self) -> bool:
        find = self.selected_find
        a3dmodel = self.selected_a3dmodel
        if find is None or a3dmodel is None:
            logger.error("No find or model selected")
            return False
        if find.is_matched:
            logger.error("Attempted to set a match for a find that already has one")
            logger.error("call clear_match_for_find first")
            return False
        find.set_match(
            self.conn,
            a3dmodel.batch_year,
            a3dmodel.batch_number,
            a3dmodel.batch_piece,
        )
        a3dmodel.matched_finds = a3dmodel.get_matches(self.conn.cursor())
        return True
