import sys
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication
import os
import pathlib

from database_tools import get_pottery_sherd_info, update_match_info

basedir = os.path.dirname(os.path.realpath(__file__))
FILE_ROOT = pathlib.Path(
    "C:\\Users\\gabe\\OneDrive - The University Of Hong Kong\\HKU\\02-Projects\\P22007-Cobb_ArchaeologyData\\Ceramics Matching\\sample"
)
# FILE_ROOT = pathlib.Path("D:\\ararat\\data\\files")
FINDS_SUBDIR = "finds/individual"
BATCH_3D_SUBDIR = "finds/3dbatch"
FINDS_PHOTO_DIR = "photos"

HEMISPHERES = ("N", "S")


class MainWindow(QMainWindow):
    """View (GUI)."""

    def __init__(self):
        """View initializer."""
        super(MainWindow, self).__init__()
        uic.loadUi("qtcreator/MainWindow.ui", self)
        self.file_root = FILE_ROOT
        self.populate_hemispheres()
        self.hemisphere_cb.currentIndexChanged.connect(self.populate_zones)
        self.zone_cb.currentIndexChanged.connect(self.populate_eastings)
        self.easting_cb.currentIndexChanged.connect(self.populate_northings)
        self.northing_cb.currentIndexChanged.connect(self.populate_contexts)
        self.context_cb.currentIndexChanged.connect(self.contextChanged)
        self.contextDisplay.setText(self.get_context_string())
        self.findsList.currentItemChanged.connect(self.load_find_images)

    def empty_cb(self, combobox):
        combobox.addItems([])
        combobox.setCurrentIndex(-1)

    def populate_hemispheres(self):
        self.hemisphere_cb.clear()
        res = [
            d.name
            for d in self.file_root.iterdir()
            if d.name in HEMISPHERES and d.is_dir()
        ]
        self.hemisphere_cb.addItems(res)
        self.set_hemisphere(0 if len(res) > 0 else -1)
        self.hemisphere_cb.setEnabled(len(res) > 1)
        self.contextDisplay.setText(self.get_context_string())

    def set_hemisphere(self, index):
        self.hemisphere_cb.setCurrentIndex(index)
        self.populate_zones()

    def populate_zones(self):
        self.zone_cb.clear()
        hemisphere = self.hemisphere_cb.currentText()
        zone_root = self.file_root / hemisphere
        res = [d.name for d in zone_root.iterdir() if d.is_dir() and d.name.isdigit()]
        self.zone_cb.addItems(res)
        self.zone_cb.setEnabled(len(res) > 1)
        self.set_zone(0 if len(res) > 0 else -1)

    def set_zone(self, index):
        self.zone_cb.setCurrentIndex(index)
        self.populate_eastings()

    def populate_eastings(self):
        self.easting_cb.clear()
        hemisphere = self.hemisphere_cb.currentText()
        zone = self.zone_cb.currentText()
        eastings_root = self.file_root / hemisphere / zone
        res = [
            d.name for d in eastings_root.iterdir() if d.is_dir() and d.name.isdigit()
        ]
        self.easting_cb.addItems(res)
        self.set_easting(0 if len(res) > 0 else -1)
        self.easting_cb.setEnabled(len(res) > 1)

    def set_easting(self, index):
        self.easting_cb.setCurrentIndex(index)
        self.populate_northings()

    def populate_northings(self):
        self.northing_cb.clear()
        northings_root = (
            self.file_root
            / self.hemisphere_cb.currentText()
            / self.zone_cb.currentText()
            / self.easting_cb.currentText()
        )
        res = [
            d.name for d in northings_root.iterdir() if d.is_dir() and d.name.isdigit()
        ]
        self.northing_cb.addItems(res)
        self.set_northing(0 if len(res) > 0 else -1)
        self.northing_cb.setEnabled(len(res) > 1)

    def set_northing(self, index):
        self.northing_cb.setCurrentIndex(index)
        self.populate_contexts()

    def populate_contexts(self):
        self.context_cb.clear()
        contexts_root = (
            self.file_root
            / self.hemisphere_cb.currentText()
            / self.zone_cb.currentText()
            / self.easting_cb.currentText()
            / self.northing_cb.currentText()
        )
        res = [
            d.name for d in contexts_root.iterdir() if d.is_dir() and d.name.isdigit()
        ]
        self.context_cb.addItems(res)
        self.set_context(0 if len(res) > 0 else -1)
        self.context_cb.setEnabled(len(res) > 1)
        self.populate_finds()

    def set_context(self, index):
        self.context_cb.setCurrentIndex(index)

    def get_context_string(self):
        """Return a string representing the full designation of the current context
        as utm_hemisphere-utm_zone-utm_easting-utm_northing-context_number

        Returns:
            str: The full designation of the currently selected context
        """
        hzenc = [
            self.hemisphere_cb.currentText(),
            self.zone_cb.currentText(),
            self.easting_cb.currentText(),
            self.northing_cb.currentText(),
            self.context_cb.currentText(),
        ]
        return "-".join(hzenc)

    def get_context_dir(self):
        res = (
            FILE_ROOT
            / self.hemisphere_cb.currentText()
            / self.zone_cb.currentText()
            / self.easting_cb.currentText()
            / self.northing_cb.currentText()
            / self.context_cb.currentText()
        )
        if not res.exists():
            self.statusLabel.setText(f"{res} does not exist!")
            return pathlib.Path()
        return res

    def contextChanged(self):
        self.contextDisplay.setText(self.get_context_string())
        self.populate_finds()

    def populate_finds(self):
        self.findsList.clear()
        context_dir = self.get_context_dir()
        finds_dir = context_dir / FINDS_SUBDIR
        finds = [d.name for d in finds_dir.iterdir() if d.name.isdigit()]
        finds.sort(key=lambda f: int(f))
        self.findsList.addItems(finds)

    def load_find_images(self):
        try:
            find_num = self.findsList.currentItem().text()
        except AttributeError:
            self.findFrontPhoto_l.clear()
            self.findBackPhoto_l.clear()
            return
        photos_dir = self.get_context_dir() / FINDS_SUBDIR / find_num / FINDS_PHOTO_DIR
        front_photo = QImage(str(photos_dir / "1.jpg"))
        back_photo = QImage(str(photos_dir / "2.jpg"))
        self.findFrontPhoto_l.setPixmap(
            QPixmap.fromImage(front_photo).scaledToWidth(self.findFrontPhoto_l.width())
        )
        self.findBackPhoto_l.setPixmap(
            QPixmap.fromImage(back_photo).scaledToWidth(self.findBackPhoto_l.width())
        )


def main():
    """Main function."""
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # Show the calculator's GUI
    main = MainWindow()
    main.show()
    # Execute the calculator's main loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
