# In MVP, Model View Presenter architecture, Model represents the data in the application.
import logging
from operator import attrgetter
from typing import List, Dict

from diskcache import Cache
import open3d as o3d
import cv2


from model.mixins.file_IO import FileIOMixin
from model.mixins.database import DatabaseMixin
from model.mixins.initial_load import InitialLoadMixin
from model.mixins.copy_file import CopyFileMixin
from model.constants import BASE_DATA_DIR
from model.models import SpatialContext, A3DModel, ObjectFind
from model.measure.segmentation import MaskPredictor
from model.measure.similarity import calculate_similarity
from model.workers.measure_find_worker import MeasureFindWorker

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

    def __init__(self, skip_ply=False):
        super().__init__()

        self.cv2_cache = Cache("./cache/cache_models")
        self.measure_cache = Cache("./cache/measure_cache")

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

        # create an invisible o3d visualizer for measuring the 3d models
        if not skip_ply:
            self.ply_window = o3d.visualization.Visualizer()
            self.ply_window.create_window(visible=False)
            self.ply_window.get_render_option().light_on = False
            self.ply_window.get_render_option().point_size = 20
        else:
            self.ply_window = None

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

    def load_finds(self, color_grid: str) -> List[MeasureFindWorker]:
        if color_grid.lower() == "default":
            cg = self.predictors["colorgrid"]
        elif color_grid.lower() == "24colorcard":
            cg = self.predictors["colorgrid_24"]
        else:
            raise ValueError(f"Invalid color grid type {color_grid}")

        self.finds_dict = {
            f.find_number: f
            for f in self.selected_context.list_finds(self.conn.cursor())
        }
        self.selected_find_number = (
            list(self.finds_dict.keys())[0] if self.finds_dict else None
        )
        worker = MeasureFindWorker(
            self.finds_dict.values(),
            self.predictors["ceramics"],
            cg,
            self.measure_cache,
        )
        return worker
        # logger.info("In main_model - Measuring finds")
        # for f in self.finds_list:
        #     # f.set_features(self.predictors["ceramics"], self.cv2_cache)
        #     f.measure(self.predictors["ceramics"], cg, self.measure_cache)

    def list_finds(self, min_find=0, max_find=99999):
        if not self.finds_dict:
            return []
        return sorted(
            [
                f
                for f in self.finds_dict.values()
                if min_find <= f.find_number <= max_find
            ],
            key=attrgetter("find_number"),
        )

    def load_a3dmodels(self):
        self.a3dmodels_dict = {str(m): m for m in self.selected_context.list_models()}
        self.selected_a3dmodel_str = (
            list(self.a3dmodels_dict.keys())[0] if self.a3dmodels_dict else None
        )
        logger.info("In main_model - Measuring 3d models")
        for m in self.a3dmodels_list:
            m.matched_finds = m.get_matches(self.conn.cursor())
            # m.set_features(self.ply_window, self.cv2_cache)
            # m.measure(self.ply_window, self.measure_cache)

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

    def list_a3dmodels_by_similarity_cv2(self, find_number):
        """This is too slow for now. cv2 is not using the GPU. Need to fix

        Args:
            find_number (int): the number for the find in the selected context

        Returns:
            List[A3dmodels]: A list of the A3dmodels sorted by similarity to the find
        """
        find: ObjectFind = self.finds_dict.get(find_number, None)
        if find is None:
            logger.error("No find with number %s", find_number)
            return []
        result = []
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        if not find.has_features:
            logger.warning("No features set for find %s.", find)
            logger.warning(
                "Check that the pictures are available at %s", find.photos_path()
            )
            return self.a3dmodels_list

        for a3dmodel in self.a3dmodels_list:
            if not a3dmodel.has_features:
                result.append((0, a3dmodel))
                continue
            front_matches = bf.match(find.descriptors_front, a3dmodel.descriptors)
            back_matches = bf.match(find.descriptors_back, a3dmodel.descriptors)
            result.append((max(len(front_matches), len(back_matches)), a3dmodel))

        result.sort(key=lambda x: x[0], reverse=True)
        return [x[1] for x in result]

    def list_a3dmodels_by_similarity(self, find_number):
        find: ObjectFind = self.finds_dict.get(find_number, None)
        if find is None:
            logger.error("No find with number %s", find_number)
            return []
        result = []
        for a3dmodel in self.a3dmodels_list:
            if not a3dmodel.is_measured:
                result.append((-1.0, a3dmodel))
            else:
                sim = calculate_similarity(a3dmodel, find)
                result.append((sim, a3dmodel))

        result.sort(key=lambda x: x[0])
        return [x[1] for x in result]
