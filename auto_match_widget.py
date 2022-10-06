from genericpath import exists
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal, QRunnable, Qt
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QScrollArea,
    QGroupBox,
    QFormLayout,
    QProgressBar,
    QLabel,
    QMessageBox,
)
from PyQt5.QtGui import QImage, QPixmap
import os
from pathlib import *
from sift_matching import *
import cv2
from threed_2_2d import open_interactive_model, process_one_batch


class auto_match_widget(QWidget):
    def __init__(self, main_widget):
        QWidget.__init__(self)
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)

        self.main_widget = main_widget
        self.curr_context_path = main_widget.cur_context_individual_path
        self.path_img_frt = main_widget.path_img_frt
        self.path_img_back = main_widget.path_img_back

        self.button_find = QPushButton(self)
        self.button_find.setText("find")
        self.button_find.clicked.connect(self.onStart)

        self.pool = QThreadPool.globalInstance()

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)

        self.groupBox = QGroupBox()
        self.scroll_area_layout = QFormLayout()
        self.groupBox.setLayout(self.scroll_area_layout)
        self.scroll.setWidget(self.groupBox)

        self.mainlayout.addWidget(self.button_find)
        self.mainlayout.addWidget(self.scroll)

    def update_auto_match_area(self):
        self.sorted_target_list = self.runnable.output
        self.progressBar.setValue(0)
        self.scroll_area_layout = QFormLayout()

        i = 0
        for sorted_target in self.sorted_target_list:

            new_candidate_card = candidate_card(
                self.main_widget,
                sorted_target[-2],
                sorted_target[-1],
                sorted_target[2],
                sorted_target[1],
                sorted_target[0],
            )
            self.scroll_area_layout.addRow(new_candidate_card)
            i = i + 1
            self.progressBar.setValue(int(100 * i / len(self.sorted_target_list)))

        self.mainlayout.removeWidget(self.progressBar)
        self.mainlayout.removeWidget(self.scroll)
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.groupBox = QGroupBox()
        self.groupBox.setLayout(self.scroll_area_layout)
        self.scroll.setWidget(self.groupBox)
        self.mainlayout.addWidget(self.scroll)

    def onStart(self):

        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.setStyleSheet("""QProgressBar {text-align: center; }""")
        self.mainlayout.insertWidget(1, self.progressBar)

        self.runnable = Runnable(self.main_widget)
        self.runnable.notifyProgress.progress.connect(self.onProgress)
        self.runnable.notifyFinished.finished.connect(self.update_auto_match_area)
        self.runnable.notifyError.error.connect(self.message)
        self.pool.start(self.runnable)

    def onProgress(self, i):
        self.progressBar.setValue(i)

    def message(self, error_batches):
        QMessageBox.information(
            self,
            "Warning",
            "3d models not finished, check the folder for: " + error_batches + " ",
        )


class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)


class Runnable(QRunnable):
    notifyProgress = WorkerSignals()
    notifyFinished = WorkerSignals()
    notifyError = WorkerSignals()

    def __init__(self, main_widget):

        super().__init__()
        self.main_widget = main_widget
        self.path_img_frt = main_widget.path_img_frt
        self.path_img_back = main_widget.path_img_back
        self.output = []

    def run(self):
        self.output = self.activate_model()

    def activate_model(self):
        proceed = True
        sorted_target_list = []
        # print(Path(self.curr_context_path).parents[1])
        error_batches = ""
        # check if the 3d model exists
        for one_batch in self.main_widget.suggested_batches:
            model_folder_path = Path(
                self.main_widget.cur_context_3dbatch_path
            ).joinpath(one_batch, "registration_reso1_maskthres242", "final_output")
            ply_file_path = model_folder_path.joinpath("piece_0_world.ply")

            if not ply_file_path.exists():
                error_batches = error_batches + " " + one_batch
                proceed = False
            else:
                continue

        if not proceed:
            print(error_batches)
            self.notifyFinished.finished.emit()
            self.notifyError.error.emit(error_batches)
            return sorted_target_list

        # if true check if 2d projection of 3d model exists for the section,if false, generate 3d proejctions
        for one_batch in self.main_widget.suggested_batches:
            model_folder_path = Path(
                self.main_widget.cur_context_3dbatch_path
            ).joinpath(one_batch, "registration_reso1_maskthres242", "final_output")
            twod_projection_folder = model_folder_path.joinpath("individual_images")

            if not twod_projection_folder.exists():
                process_one_batch(
                    Path(self.main_widget.cur_context_3dbatch_path).joinpath(one_batch)
                )
            else:
                continue

        if proceed:
            all_targets_for_context_list = read_context_targets(
                self.main_widget
            )  # Path(self.curr_context_path).parents[1]
            query_img_frt = cv2.imread(self.path_img_frt)
            query_img_back = cv2.imread(self.path_img_back)

            i = 0
            for one_target in all_targets_for_context_list:
                target_img_front = cv2.imread(str(one_target[0]))
                target_img_back = cv2.imread(str(one_target[1]))
                good_match_num = img_compare(
                    query_img_frt, target_img_front
                ) + img_compare(query_img_back, target_img_back)
                target_img_batch_num = int(((one_target[1]).parts[-6])[-3::])
                target_img_num = int((one_target[1]).parts[-2])
                sorted_target_list.append(
                    (
                        good_match_num,
                        target_img_num,
                        target_img_batch_num,
                        one_target[0],
                        one_target[1],
                    )
                )
                i = i + 1
                self.notifyProgress.progress.emit(
                    int(100 * i / len(all_targets_for_context_list))
                )

            sorted_target_list.sort(key=lambda x: x[0], reverse=True)
            self.notifyFinished.finished.emit()
            return sorted_target_list


class candidate_card(QWidget):
    def __init__(
        self,
        main_widget,
        front_img_path,
        back_img_path,
        batch_number,
        piece_number,
        match_point_number,
    ):
        QWidget.__init__(self)

        self.main_widget = main_widget
        self.batch_number = batch_number
        self.piece_number = piece_number
        self.batch_image_path = (
            str(front_img_path.parents[2]) + "\\00_corres_img_pieces.png"
        )
        self.model_path = str(
            front_img_path.parents[2]
        ) + "\\piece_{}_world.ply".format(piece_number)

        self.candidate_img_frt = QLabel(self)
        self.candidate_img_frt.setPixmap(
            QPixmap.fromImage(QImage(str(front_img_path))).scaledToHeight(220)
        )

        self.candidate_img_back = QLabel(self)
        self.candidate_img_back.setPixmap(
            QPixmap.fromImage(QImage(str(back_img_path))).scaledToHeight(220)
        )

        self.candidate_card_layout = QVBoxLayout()
        self.candidate_card_images_layout = QHBoxLayout()
        self.candidate_card_labels_layout = QHBoxLayout()
        self.candidate_buttons_layout = QVBoxLayout()

        self.candidate_batch_label = QLabel(self)
        self.candidate_batch_label.setText("Batch Number: {}".format(batch_number))
        self.candidate_batch_label.setFixedHeight(30)

        self.candidate_piece_label = QLabel(self)
        self.candidate_piece_label.setText("Piece number: {}".format(piece_number))
        self.candidate_piece_label.setFixedHeight(30)

        self.match_points_label = QLabel(self)
        self.match_points_label.setText("match points: {}".format(match_point_number))
        self.match_points_label.setFixedHeight(30)

        self.button_open_batch_image = QPushButton(self)
        self.button_open_batch_image.setText("Batch Image")
        self.button_open_batch_image.clicked.connect(self.open_batch)

        self.button_open_3d = QPushButton(self)
        self.button_open_3d.setText("3D Model")
        self.button_open_3d.clicked.connect(self.open_3d_model)

        self.button_confirm = QPushButton(self)
        self.button_confirm.setText("Update Match Info")
        self.button_confirm.clicked.connect(self.update_match_info)

        self.candidate_card_images_layout.addWidget(self.candidate_img_frt)
        self.candidate_card_images_layout.addWidget(self.candidate_img_back)
        self.candidate_card_labels_layout.addWidget(self.candidate_batch_label)
        self.candidate_card_labels_layout.addWidget(self.candidate_piece_label)
        self.candidate_card_labels_layout.addWidget(self.match_points_label)
        self.candidate_buttons_layout.addWidget(self.button_open_batch_image)
        self.candidate_buttons_layout.addWidget(self.button_open_3d)
        self.candidate_buttons_layout.addWidget(self.button_confirm)

        self.candidate_card_layout.addLayout(self.candidate_card_images_layout)
        self.candidate_card_layout.addLayout(self.candidate_card_labels_layout)
        self.candidate_card_layout.addLayout(self.candidate_buttons_layout)
        self.setLayout(self.candidate_card_layout)

    def open_batch(self):
        os.startfile(self.batch_image_path)

    def open_3d_model(self):
        open_interactive_model(self.model_path)

    def update_match_info(self):
        self.main_widget.sherd_input.setText(str(self.piece_number))
        self.main_widget.batch_input.setText(str(self.batch_number))
