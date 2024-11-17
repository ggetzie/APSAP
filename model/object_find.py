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
        return all([self.batch_year, self.batch_number, self.batch_piece])

    def set_match(self, batch_year: int, batch_number: int, batch_piece: int):
        self._batch_year = batch_year
        self._batch_number = batch_number
        self._batch_piece = batch_piece
