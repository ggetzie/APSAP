import logging
import pathlib
import re
from typing import List

import psycopg2

from model.constants import BASE_DATA_DIR

logger = logging.getLogger(__name__)


class InvalidSpatialContextString(Exception):
    pass


def parse_context_string(context_str: str):
    m = re.match(r"([NS])-(\d+)-(\d+)-(\d+)-(\d+)", context_str)
    if not m:
        raise InvalidSpatialContextString
    return (
        m.group(1),
        m.group(2),
        m.group(3),
        m.group(4),
        m.group(5),
    )


class SpatialContext:

    def __init__(
        self,
        utm_hemisphere: str,
        utm_zone: int,
        area_utm_easting_meters: int,
        area_utm_northing_meters: int,
        context_number: int,
    ):
        self.utm_hemisphere = utm_hemisphere
        self.utm_zone = utm_zone
        self.area_utm_easting_meters = area_utm_easting_meters
        self.area_utm_northing_meters = area_utm_northing_meters
        self.context_number = context_number

    def __str__(self):
        return (
            f"{self.utm_hemisphere}-"
            f"{self.utm_zone}-"
            f"{self.area_utm_easting_meters}-"
            f"{self.area_utm_northing_meters}-"
            f"{self.context_number}"
        )

    def __repr__(self):
        return f"<SpatialContext {self}>"

    @property
    def path(self) -> pathlib.Path:
        return (
            BASE_DATA_DIR
            / self.utm_hemisphere
            / str(self.utm_zone)
            / str(self.area_utm_easting_meters)
            / str(self.area_utm_northing_meters)
            / str(self.context_number)
        )

    @property
    def finds_folder(self) -> pathlib.Path:
        return self.path / "finds" / "individual"

    @property
    def models_folder(self) -> pathlib.Path:
        return self.path / "finds" / "3dbatch"

    def list_find_dirs(self):
        if not self.finds_folder.exists():
            return []
        return sorted(
            [
                d.name
                for d in self.finds_folder.iterdir()
                if d.is_dir() and d.name.isnumeric()
            ],
            key=int,
        )

    def list_batch_years(self):
        if not self.models_folder.exists():
            return []
        return sorted(
            [
                int(d.name)
                for d in self.models_folder.iterdir()
                if d.is_dir() and re.match(r"\d{4}", d.name)
            ]
        )

    def list_batch_numbers(self, year: str) -> List[str]:
        folder = self.models_folder / year
        if not folder.exists():
            return []
        return sorted(
            [
                int(d.name.split("_")[1])
                for d in folder.iterdir()
                if d.is_dir() and re.match(r"^batch_\d{3}$", d.name)
            ]
        )

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
                self.utm_hemisphere,
                self.utm_zone,
                self.area_utm_easting_meters,
                self.area_utm_northing_meters,
                self.context_number,
                min_find,
                max_find,
            ),
        )
        rows = cursor.fetchall()

        result = [
            ObjectFind(
                utm_hemisphere=self.utm_hemisphere,
                utm_zone=self.utm_zone,
                area_utm_easting_meters=self.area_utm_easting_meters,
                area_utm_northing_meters=self.area_utm_northing_meters,
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
        for year_dir in self.models_folder.iterdir():
            if not (year_dir.is_dir() and re.match(r"\d{4}", year_dir.name)):
                continue
            batch_year = year_dir.name
            for num_dir in year_dir.iterdir():
                if not (num_dir.is_dir() and re.match(r"^batch_\d{3}$", num_dir.name)):
                    continue
                batch_number = int(num_dir.name.split("_")[1])
                piece_dir = num_dir / "registration_reso1_maskthres242" / "final_output"
                number_set = set()
                for piece_file in piece_dir.glob("piece_*.ply"):
                    m = re.match(r"piece_(\d+)_", piece_file.name)
                    if not m:
                        continue
                    piece_number = int(m.group(1))
                    number_set.add(piece_number)
                piece_numbers = sorted(list(number_set))

                for piece_number in piece_numbers:
                    a3dmodel = A3DModel(
                        spatial_context=self,
                        batch_year=int(batch_year),
                        batch_number=batch_number,
                        batch_piece=int(piece_number),
                    )
                    result.append(a3dmodel)
        logger.info("Found %d models in %s", len(result), self.models_folder)
        return result


TEST_SC = SpatialContext("N", 38, 478130, 4419430, 109)


def year_batch_piece_str(year: int, batch: int, piece: int) -> str:
    return f"{year}-{batch:>03}-{piece:>02}"


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
        self.material = material
        self.category = category
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

    @property
    def is_matched(self) -> bool:
        return (
            self._batch_year is not None
            and self._batch_number is not None
            and self._batch_piece is not None
        )

    def set_match(self, conn, batch_year: int, batch_number: int, batch_piece: int):
        if (
            self._batch_year == batch_year
            and self._batch_number == batch_number
            and self._batch_piece == batch_piece
        ):
            return  # no changes
        self._batch_year = batch_year
        self._batch_number = batch_number
        self._batch_piece = batch_piece
        logger.info("Matching %s to %s", self, self.get_match_str())
        logger.info("Updating database")
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
        cursor = conn.cursor()
        try:
            cursor.execute(
                query,
                (
                    self._batch_year,
                    self._batch_number,
                    self._batch_piece,
                    self._utm_hemisphere,
                    self._utm_zone,
                    self._area_utm_easting_meters,
                    self._area_utm_northing_meters,
                    self._context_number,
                    self.find_number,
                ),
            )
            logger.info("Matched %s to %s", self, self.get_match_str())
            conn.commit()
        except psycopg2.Error as e:
            logger.error("Failed to match %s to %s", self, self.get_match_str())
            logger.error(e)
            conn.rollback()
        finally:
            cursor.close()

    def clear_match(self, cursor):
        if not self.is_matched:
            return
        logger.info("Clearing match for %s", self)
        self._batch_number = None
        self._batch_piece = None
        self.set_match(cursor, self._batch_year, None, None)

    def get_match(self):
        return self._batch_year, self._batch_number, self._batch_piece

    def get_match_str(self):
        if self.is_matched:
            return year_batch_piece_str(
                self._batch_year, self._batch_number, self._batch_piece
            )
        return ""

    def directory(self) -> pathlib.Path:
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
        )

    def photos_path(self) -> pathlib.Path:
        return self.directory() / "photos"

    def photo_path(self, side="front") -> pathlib.Path:
        name = "1.jpg" if side == "front" else "2.jpg"
        return self.photos_path() / name

    def has_photos(self) -> bool:
        front_exists = (self.photos_path() / "1.jpg").exists()
        back_exists = (self.photos_path() / "2.jpg").exists()
        return front_exists and back_exists

    def models_directory(self):
        return self.directory() / "3d" / "gp"


class A3DModel:

    def __init__(
        self,
        batch_year: int,
        batch_number: int,
        batch_piece: int,
        spatial_context: SpatialContext,
    ):
        self.spatial_context = spatial_context
        self.batch_year = batch_year
        self.batch_number = batch_number
        self.batch_piece = batch_piece

        # the find numbers that are matched to this model
        self.matched_finds: List[int] = []

    def __str__(self):
        return year_batch_piece_str(
            self.batch_year, self.batch_number, self.batch_piece
        )

    def __repr__(self):
        return f"<A3DModel {self}>"

    @property
    def is_matched(self):
        return len(self.matched_finds) > 0

    @property
    def cache_key(self) -> str:
        return f"{self.spatial_context}-{self}"

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
        """There are three .ply files for each model:
        - full:   piece_1_world.ply
        - mesh:   piece_1_world_sample0_3_mesh.ply
        - sample: piece_1_world_sample0_3.ply

        Args:
            filetype (str, optional): Which file to get Defaults to "full".

        Returns:
            pathlib.Path: Path to the selected file
        """
        if filetype == "full":
            return self.get_folder() / f"piece_{self.batch_piece}_world.ply"
        if filetype == "mesh":
            for f in self.list_files():
                if "mesh" in f.name:
                    return f
        if filetype == "sample":
            for f in self.list_files():
                if "sample" in f.name and "mesh" not in f.name:
                    return f
        return None

    def get_matches(self, cursor):
        query = """
        SELECT find_number
        FROM object.finds
        WHERE
        utm_hemisphere = %s AND
        utm_zone = %s AND
        area_utm_easting_meters = %s AND
        area_utm_northing_meters = %s AND
        context_number = %s AND
        "3d_batch_year" = %s AND
        "3d_batch_number" = %s AND
        "3d_batch_piece" = %s;
        """
        cursor.execute(
            query,
            (
                self.spatial_context.utm_hemisphere,
                self.spatial_context.utm_zone,
                self.spatial_context.area_utm_easting_meters,
                self.spatial_context.area_utm_northing_meters,
                self.spatial_context.context_number,
                self.batch_year,
                self.batch_number,
                self.batch_piece,
            ),
        )
        rows = cursor.fetchall()
        result = [row[0] for row in rows]
        if len(result) > 1:
            logger.error("Found %d finds matched to %s! %s", len(result), self, result)
        return result
