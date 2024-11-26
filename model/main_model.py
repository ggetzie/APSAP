# In MVP, Model View Presenter architecture, Model represents the data in the application.
import logging
from operator import attrgetter
from typing import List, Dict
from model.mixins.file_IO import FileIOMixin
from model.mixins.database import DatabaseMixin
from model.mixins.initial_load import InitialLoadMixin
from model.mixins.copy_file import CopyFileMixin
from model.constants import BASE_DATA_DIR
from model.models import SpatialContext, A3DModel, ObjectFind, year_batch_piece_str
from model.measure.segmentation import MaskPredictor

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

        self.predictors = {
            "colorgrid": MaskPredictor(mask_type="colorgrid"),
            "colorgrid_24": MaskPredictor(mask_type="colorgrid_24"),
            "ceramics": MaskPredictor(mask_type="ceramics"),
        }

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
        self.hemisphere_list: List[str] = []
        self.selected_hemisphere_idx = None

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

    def get_hemispheres(self):
        self.hemisphere_list = sorted(
            [
                d.name
                for d in BASE_DATA_DIR.iterdir()
                if d.is_dir() and d.name in ["N", "S"]
            ]
        )

    def set_hemispheres_index(self, idx):
        self.selected_hemisphere_idx = idx

    def get_zones(self):
        try:
            hemisphere = self.hemisphere_list[self.selected_hemisphere_idx]
        except IndexError:
            self.zone_list = []
            return
        hemisphere_dir = BASE_DATA_DIR / hemisphere
        self.zone_list = sorted(
            [
                d.name
                for d in hemisphere_dir.iterdir()
                if d.is_dir() and d.name.isnumeric()
            ],
            key=int,
        )

    def set_zone_index(self, idx):
        self.selected_zone_idx = idx

    def get_eastings(self):
        try:
            hemisphere = self.hemisphere_list[self.selected_hemisphere_idx]
            zone = self.zone_list[self.selected_zone_idx]
        except IndexError:
            self.easting_list = []
            return

        zone_dir = BASE_DATA_DIR / hemisphere / zone
        self.easting_list = sorted(
            [d.name for d in zone_dir.iterdir() if d.is_dir() and d.name.isnumeric()],
            key=int,
        )

    def set_easting_index(self, idx):
        self.selected_easting_idx = idx

    def get_northings(self) -> List[str]:
        try:
            hemisphere = self.hemisphere_list[self.selected_hemisphere_idx]
            zone = self.zone_list[self.selected_zone_idx]
            easting = self.easting_list[self.selected_easting_idx]
        except IndexError:
            self.northing_list = []
            return

        easting_dir = BASE_DATA_DIR / hemisphere / zone / easting
        self.northing_list = sorted(
            [
                d.name
                for d in easting_dir.iterdir()
                if d.is_dir() and d.name.isnumeric()
            ],
            key=int,
        )

    def set_northing_index(self, idx):
        self.selected_northing_idx = idx

    def get_contexts(self):
        try:
            hemisphere = self.hemisphere_list[self.selected_hemisphere_idx]
            zone = self.zone_list[self.selected_zone_idx]
            easting = self.easting_list[self.selected_easting_idx]
            northing = self.northing_list[self.selected_northing_idx]
        except IndexError:
            self.context_list = []
            return

        self.context_list = sorted(
            [
                SpatialContext(
                    utm_hemisphere=hemisphere,
                    utm_zone=int(zone),
                    area_utm_easting_meters=int(easting),
                    area_utm_northing_meters=int(northing),
                    context_number=int(d.name),
                )
                for d in (
                    BASE_DATA_DIR / hemisphere / zone / easting / northing
                ).iterdir()
                if d.is_dir() and d.name.isnumeric()
            ],
            key=attrgetter("context_number"),
        )

    def set_context_index(self, idx):
        self.selected_context_idx = idx

    def load_finds(self):
        self.finds_dict = {
            f.find_number: f
            for f in self.selected_context.list_finds(self.conn.cursor())
        }
        self.selected_find_number = (
            list(self.finds_dict.keys())[0] if self.finds_dict else None
        )

    def load_a3dmodels(self):
        self.a3dmodels_dict = {str(m): m for m in self.selected_context.list_models()}
        self.selected_a3dmodel_str = (
            list(self.a3dmodels_dict.keys())[0] if self.a3dmodels_dict else None
        )
        for m in self.a3dmodels_list:
            m.matched_finds = m.get_matches(self.conn.cursor())

    def get_all_matches(self):
        sc = self.selected_context
        if sc is None:
            return
        query = """
        SELECT "3d_batch_year", "3d_batch_number", "3d_batch_piece", "find_number"
        FROM object.finds
        WHERE utm_hemisphere = %s AND utm_zone = %s AND area_utm_easting_meters = %s AND area_utm_northing_meters = %s AND context_number = %s
        AND "3d_batch_year" IS NOT NULL AND "3d_batch_number" IS NOT NULL AND "3d_batch_piece" IS NOT NULL;
        """

        try:
            self.conn.cursor().execute(
                query,
                (
                    sc.utm_hemisphere,
                    sc.utm_zone,
                    sc.area_utm_easting_meters,
                    sc.area_utm_northing_meters,
                    sc.context_number,
                ),
            )
            rows = self.conn.cursor().fetchall()
        except Exception as e:
            logger.error("Error fetching matches: %s", e)
            return
        logger.info("Found %s matches", len(rows))
        for row in rows:
            a3dmodel_str = year_batch_piece_str(*row[:3])
            find_number = row[3]
            a3dmodel = self.a3dmodels_dict.get(a3dmodel_str, None)
            if a3dmodel is not None:
                a3dmodel.matched_finds.append(find_number)

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
        find: ObjectFind = self.finds_dict.get(find_number, None)
        if find is None:
            logger.debug("No find with number %s", find_number)
            return False
        old_match: A3DModel = self.a3dmodels_dict[find.get_match_str()]
        if old_match is None:
            logger.debug("No 3d model with %s", find.get_match_str())
            return False
        find.clear_match(self.conn)
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
