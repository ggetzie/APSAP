from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage, QCursor
from PyQt5.QtCore import Qt
import os
from pathlib import *
from identify_batch_range import identify_range_of_batches

basedir = os.path.dirname(os.path.realpath(__file__))


class manual_match_widget(QWidget):
    def __init__(self, main_widget):
        QWidget.__init__(self)
        layout = QVBoxLayout()
        self.setLayout(layout)

        # self.context_folder = Path(main_widget.root_path).joinpath(str(main_widget.curr_context),'finds','3dbatch','2022')

        self.context_folder = Path(main_widget.cur_context_3dbatch_path)
        batch_list = []
        # suggested_batch_list = identify_range_of_batches()
        # double check folde exists
        if not self.context_folder.exists():
            print("Batch has not finished building all the 3d models")
        else:
            batch_list = [
                batch
                for batch in self.context_folder.iterdir()
                if (
                    batch.is_dir()
                    and ("batch" in batch.stem)
                    and not ("einscan" in batch.stem)
                )
            ]  # read in all the files

        self.batch_list_widget = QListWidget()

        for batch_name in batch_list:
            if batch_name.stem in main_widget.suggested_batches:
                self.batch_list_widget.addItem(batch_name.stem + " *")
            else:
                self.batch_list_widget.addItem(batch_name.stem)

        self.batch_list_widget.itemDoubleClicked.connect(self.open_batch_image_in_gui)

        layout.addWidget(self.batch_list_widget)

        self.batch_image_display_label = QLabel()
        reference_image_path = os.path.join(
            basedir, "assets", "reference_placeholder.png"
        )
        self.batch_image_display_label.setPixmap(
            QPixmap(reference_image_path).scaledToHeight(300)
        )
        self.batch_image_display_label.setToolTip("Click to open")
        layout.addWidget(self.batch_image_display_label)

    def open_batch_image_in_gui(self, item):
        batch_reference_path = (
            str(self.context_folder)
            + "\\"
            + item.text().split(" ")[0]
            + "\\registration_reso1_maskthres242\\final_output\\00_corres_img_pieces.png"
        )
        self.myimage = QImage(batch_reference_path)
        self.batch_image_display_label.setPixmap(
            QPixmap.fromImage(self.myimage).scaledToHeight(300)
        )
        self.batch_image_display_label.mousePressEvent = (
            lambda x: self.open_batch_image(batch_reference_path)
        )
        self.batch_image_display_label.setCursor(QCursor(Qt.PointingHandCursor))

    def open_batch_image(self, path):
        os.startfile(path)
