import logging
import pathlib
import re
from typing import List

from PIL import Image
from model.constants import BASE_DATA_DIR

logger = logging.getLogger(__name__)


class SpatialContext:

    def __init__(
        self,
        utm_hemisphere: str,
        utm_zone: int,
        area_utm_easting_meters: int,
        area_utm_northing_meters: int,
        context_number: int,
    ):
        self._utm_hemisphere = utm_hemisphere
        self._utm_zone = utm_zone
        self._area_utm_easting_meters = area_utm_easting_meters
        self._area_utm_northing_meters = area_utm_northing_meters
        self.context_number = context_number

    def __str__(self):
        return (
            f"{self._utm_hemisphere}-"
            f"{self._utm_zone}-"
            f"{self._area_utm_easting_meters}-"
            f"{self._area_utm_northing_meters}-"
            f"{self.context_number}"
        )

    def __repr__(self):
        return f"<SpatialContext {self}>"

    @property
    def path(self) -> pathlib.Path:
        return (
            BASE_DATA_DIR
            / self._utm_hemisphere
            / str(self._utm_zone)
            / str(self._area_utm_easting_meters)
            / str(self._area_utm_northing_meters)
            / str(self.context_number)
        )

    @property
    def finds_folder(self) -> pathlib.Path:
        return self.path / "finds" / "individual"

    @property
    def models_folder(self) -> pathlib.Path:
        return self.path / "finds" / "3dbatch"

    def list_finds(self, cursor, min_find=0, max_find=9999):
        query = """
        SELECT find_number, material, category, "3d_batch_year", "3d_batch_number", "3d_batch_piece"
        FROM object.finds
        WHERE
        utm_hemisphere = %s AND
        utm_zone = %s AND
        area_utm_easting_meters = %s AND
        area_utm_northing_meters = %s AND
        context_number = %s AND
        find_number BETWEEN %s AND %s
        ORDER BY find_number ASC;
        """
        cursor.execute(
            query,
            (
                self._utm_hemisphere,
                self._utm_zone,
                self._area_utm_easting_meters,
                self._area_utm_northing_meters,
                self.context_number,
                min_find,
                max_find,
            ),
        )
        rows = cursor.fetchall()

        result = [
            ObjectFind(
                utm_hemisphere=self._utm_hemisphere,
                utm_zone=self._utm_zone,
                area_utm_easting_meters=self._area_utm_easting_meters,
                area_utm_northing_meters=self._area_utm_northing_meters,
                context_number=self.context_number,
                find_number=row[0],
                material=row[1],
                category=row[2],
                batch_year=row[3],
                batch_number=row[4],
                batch_piece=row[5],
            )
            for row in rows
        ]
        return result

    def list_models(self):
        result = []
        if not self.models_folder.exists():
            return result
        for batch_year_dir in self.models_folder.iterdir():
            if batch_year_dir.is_dir() and re.match(r"\d{4}", batch_year_dir.name):
                batch_year = batch_year_dir.name
                for batch_num_dir in batch_year_dir.iterdir():
                    if batch_num_dir.is_dir() and re.match(
                        r"^batch_\d{3}$", batch_num_dir.name
                    ):
                        batch_number = int(batch_num_dir.name.split("_")[1])
                        batch_piece_dir = (
                            batch_num_dir
                            / "registration_reso1_maskthres242"
                            / "final_output"
                        )
                        number_set = set()
                        for piece_file in batch_piece_dir.glob("piece_*.ply"):
                            m = re.match(r"piece_(\d+)_", piece_file.name)
                            if not m:
                                continue
                            piece_number = int(m.group(1))
                            number_set.add(piece_number)
                        piece_numbers = sorted(list(number_set))

                        for piece_number in piece_numbers:
                            result.append(
                                A3DModel(
                                    batch_year=int(batch_year),
                                    batch_number=batch_number,
                                    batch_piece=int(piece_number),
                                    spatial_context=self,
                                )
                            )

        return result


TEST_SC = SpatialContext("N", 38, 478130, 4419430, 109)


class ObjectFind:

    def __init__(
        self,
        utm_hemisphere: str,
        utm_zone: int,
        area_utm_easting_meters: int,
        area_utm_northing_meters: int,
        context_number: int,
        find_number: int,
        material: str = "",
        category: str = "",
        batch_year: int = None,
        batch_number: int = None,
        batch_piece: int = None,
    ):
        self._utm_hemisphere = utm_hemisphere
        self._utm_zone = utm_zone
        self._area_utm_easting_meters = area_utm_easting_meters
        self._area_utm_northing_meters = area_utm_northing_meters
        self._context_number = context_number
        self.find_number = find_number
        self._material = material
        self._category = category
        self._batch_year = batch_year
        self._batch_number = batch_number
        self._batch_piece = batch_piece

    def __str__(self):
        return (
            f"{self._utm_hemisphere}-"
            f"{self._utm_zone}-"
            f"{self._area_utm_easting_meters}-"
            f"{self._area_utm_northing_meters}-"
            f"{self._context_number}-{self.find_number}"
        )

    def __repr__(self):
        return f"<ObjectFind {self}>"

    def is_matched(self) -> bool:
        return (
            self._batch_year is not None
            and self._batch_number is not None
            and self._batch_piece is not None
        )

    def set_match(self, cursor, batch_year: int, batch_number: int, batch_piece: int):
        if (
            self._batch_year == batch_year
            and self._batch_number == batch_number
            and self._batch_piece == batch_piece
        ):
            return  # no changes
        self._batch_year = batch_year
        self._batch_number = batch_number
        self._batch_piece = batch_piece
        query = """
        UPDATE object.finds
        SET "3d_batch_year" = %s, "3d_batch_number" = %s, "3d_batch_piece" = %s
        WHERE
        utm_hemisphere = %s AND
        utm_zone = %s AND
        area_utm_easting_meters = %s AND
        area_utm_northing_meters = %s AND
        context_number = %s AND
        find_number = %s;
        """
        cursor.execute(
            query,
            (
                batch_year,
                batch_number,
                batch_piece,
                self._utm_hemisphere,
                self._utm_zone,
                self._area_utm_easting_meters,
                self._area_utm_northing_meters,
                self._context_number,
                self.find_number,
            ),
        )

    def get_match(self):
        return self._batch_year, self._batch_number, self._batch_piece

    def get_match_str(self):
        if self.is_matched():
            return f"{self._batch_year}-{self._batch_number}-{self._batch_piece}"
        return ""

    def photos_path(self) -> pathlib.Path:
        return (
            BASE_DATA_DIR
            / self._utm_hemisphere
            / str(self._utm_zone)
            / str(self._area_utm_easting_meters)
            / str(self._area_utm_northing_meters)
            / str(self._context_number)
            / "finds"
            / "individual"
            / str(self.find_number)
            / "photos"
        )

    def has_photos(self) -> bool:
        front_exists = (self.photos_path() / "1.jpg").exists()
        back_exists = (self.photos_path() / "2.jpg").exists()
        return front_exists and back_exists

    def open_photo(self, side="front"):
        name = "1.jpg" if side == "front" else "2.jpg"
        path = self.photos_path() / name
        return Image.open(path).resize((450, 300), Image.LANCZOS).convert("RGB")


class A3DModel:

    def __init__(
        self,
        batch_year: int,
        batch_number: int,
        batch_piece: int,
        spatial_context: SpatialContext,
        object_find: ObjectFind = None,
    ):
        self.batch_year = batch_year
        self.batch_number = batch_number
        self.batch_piece = batch_piece
        self.spatial_context = spatial_context
        self.object_find = object_find

    def __str__(self):
        return f"{self.batch_year}-{self.batch_number:>03}-{self.batch_piece:>02}"

    def __repr__(self):
        return f"<A3DModel {self}>"

    def is_matched(self) -> bool:
        return self.object_find is not None and self.object_find.is_matched()

    def get_folder(self):
        return (
            self.spatial_context.models_folder
            / str(self.batch_year)
            / f"batch_{self.batch_number:>03}"
            / "registration_reso1_maskthres242"
            / "final_output"
        )

    def list_files(self) -> List[pathlib.Path]:
        return list(self.get_folder().glob(f"piece_{self.batch_piece}_*.ply"))

    def get_file(self, filetype="full") -> pathlib.Path:
        if filetype == "full":
            return self.get_folder() / f"piece_{self.batch_piece:>03}_world.ply"
        if filetype == "mesh":
            for f in self.list_files():
                if "mesh" in f.name:
                    return f
        if filetype == "sample":
            for f in self.list_files():
                if "sample" in f.name and "mesh" not in f.name:
                    return f
        return None
    