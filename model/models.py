import logging
import pathlib

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
        self._context_number = context_number

    def __str__(self):
        return (
            f"{self._utm_hemisphere}-"
            f"{self._utm_zone}-"
            f"{self._area_utm_easting_meters}-"
            f"{self._area_utm_northing_meters}-"
            f"{self._context_number}"
        )

    @property
    def path(self) -> pathlib.Path:
        return (
            BASE_DATA_DIR
            / self._utm_hemisphere
            / self.utm_zone
            / self._area_utm_easting_meters
            / self._area_utm_northing_meters
            / self._context_number
        )

    @property
    def finds_folder(self) -> pathlib.Path:
        return self.path / "finds" / "individual"

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
                self._context_number,
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
                context_number=self._context_number,
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
        self._find_number = find_number
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
            f"{self._context_number}{self._find_number}"
        )

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
                self._find_number,
            ),
        )

    def get_match(self):
        return self._batch_year, self._batch_number, self._batch_piece

    def photos_path(self) -> pathlib.Path:
        return (
            BASE_DATA_DIR
            / self._utm_hemisphere
            / self._utm_zone
            / self._area_utm_easting_meters
            / self._area_utm_northing_meters
            / self._context_number
            / "finds"
            / "individual"
            / self._find_number
            / "photos"
        )

    def open_photo(self, side="front"):
        name = "1.jpg" if side == "front" else "2.jpg"
        path = self.photos_path() / name
        return Image.open(path).resize((450, 300), Image.LANCZOS).convert("RGB")
