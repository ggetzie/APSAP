from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
from pathlib import *
from sift_matching import *
import cv2
import sys
from alive_progress import alive_bar

class auto_match_widget(QWidget):
    def __init__(self,curr_context_path,path_img_frt,path_img_back):
        QWidget.__init__(self)
        self.mainlayout = QVBoxLayout()
        self.setLayout(self.mainlayout)

        self.curr_context_path = curr_context_path
        self.path_img_frt = path_img_frt
        self.path_img_back = path_img_back

        self.button_find = QPushButton(self)
        self.button_find.setText('find')
        self.button_find.clicked.connect(self.activate_model)

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

    def activate_model(self):
        proceed = True
        print(Path(self.curr_context_path).parents[1])
        if proceed:
            all_targets_for_context_list = read_context_targets(Path(self.curr_context_path).parents[1])

            query_img_frt = cv2.imread(self.path_img_frt)
            query_img_back = cv2.imread(self.path_img_back)

            sorted_target_list = []
            with alive_bar(len(all_targets_for_context_list), force_tty = True) as bar:
                for one_target in all_targets_for_context_list:

                    target_img_front = cv2.imread(str(one_target[0]))
                    target_img_back = cv2.imread(str(one_target[1]))

                    good_match_num = img_compare(query_img_frt, target_img_front) + img_compare(query_img_back, target_img_back)

                    target_img_batch_num = int(((one_target[1]).parts[-6])[-3::])
                    
                    target_img_num = int((one_target[1]).parts[-2])

                    sorted_target_list.append((good_match_num, target_img_num, target_img_batch_num, one_target[0], one_target[1]))

                    bar()

            sorted_target_list.sort(key=lambda x: x[0],reverse=True)

            self.mainlayout.removeWidget(self.scroll)
            self.scroll = QScrollArea()
            self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll.setWidgetResizable(True)
            self.scroll_area_layout =  QFormLayout()
            self.groupBox = QGroupBox()

            with alive_bar(len(sorted_target_list), force_tty = True) as bar:
                for sorted_target in sorted_target_list:

                    self.candidate_img_frt = QLabel(self)
                    self.candidate_img_frt.setPixmap(QPixmap(str(sorted_target[-2])).scaledToHeight(150))
                    #self.candidate_img_frt.mousePressEvent = (lambda x: self.open_image(str(sorted_target[-2].parents[2]) + "\\00_corres_img_pieces.png"))

                    self.candidate_img_back = QLabel(self)
                    self.candidate_img_back.setPixmap(QPixmap(str(sorted_target[-1])).scaledToHeight(150))
                    # self.candidate_img_frt.mousePressEvent = (lambda x: self.open_image(str(sorted_target[-2].parents[2]) + "\\00_corres_img_pieces.png"))

                    self.candidate_card_layout = QVBoxLayout()
                    self.candidate_card_images_layout = QHBoxLayout()
                    self.candidate_card_labels_layout = QHBoxLayout()
                    
                    self.candidate_batch_label = QLabel(self)
                    self.candidate_batch_label.setText("Batch Number: {}".format(sorted_target[2]))
                    self.candidate_batch_label.setFixedHeight(30)

                    self.candidate_piece_label = QLabel(self)
                    self.candidate_piece_label.setText("Piece number: {}".format(sorted_target[1]))
                    self.candidate_piece_label.setFixedHeight(30)


                    self.match_points_label = QLabel(self)
                    self.match_points_label.setText("match points: {}".format(sorted_target[0]))
                    self.match_points_label.setFixedHeight(30)

                    self.candidate_card_images_layout.addWidget(self.candidate_img_frt)
                    self.candidate_card_images_layout.addWidget(self.candidate_img_back)
                    self.candidate_card_labels_layout.addWidget(self.candidate_batch_label)
                    self.candidate_card_labels_layout.addWidget(self.candidate_piece_label)
                    self.candidate_card_labels_layout.addWidget(self.match_points_label)

                    self.candidate_card_layout.addLayout(self.candidate_card_images_layout)
                    self.candidate_card_layout.addLayout(self.candidate_card_labels_layout)
                    
                    self.scroll_area_layout.addRow(self.candidate_card_layout)

                    bar()


            self.groupBox.setLayout(self.scroll_area_layout)
            self.scroll.setWidget(self.groupBox)
            self.mainlayout.addWidget(self.scroll)
            
