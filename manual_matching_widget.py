from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
from pathlib import *

class manual_match_widget(QWidget):
    def __init__(self,context_path,context_number):
        QWidget.__init__(self)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.context_folder = Path(context_path).joinpath(str(context_number),'finds','3dbatch','2022')

        batch_list = []
        #double check folde exists 
        if not self.context_folder.exists():
            print("Batch has not finished building all the 3d models")
        else:
            batch_list = [batch for batch in self.context_folder.iterdir() if (batch.is_dir() and ('batch' in batch.stem) and not ('einscan' in batch.stem)) ] #read in all the files 

        self.batch_list_widget = QListWidget()

        for batch_name in batch_list:
            self.batch_list_widget.addItem(batch_name.stem)

        self.batch_list_widget.itemDoubleClicked.connect(self.open_batch_image_in_gui)

        layout.addWidget(self.batch_list_widget)

        self.batch_image_display_label = QLabel()
        self.batch_image_display_label.setPixmap(QPixmap('.\\assets\\reference_placeholder.png').scaledToHeight(300))
        self.batch_image_display_label.setToolTip("Click to open")
        layout.addWidget(self.batch_image_display_label)

    def open_batch_image_in_gui(self,item):
        batch_reference_path = str(self.context_folder) + "\\" + item.text() + "\\registration_reso1_maskthres242\\final_output\\00_corres_img_pieces.png"
        self.myimage = QImage(batch_reference_path)
        self.batch_image_display_label.setPixmap(QPixmap.fromImage(self.myimage).scaledToHeight(300))
        self.batch_image_display_label.mousePressEvent = (lambda x: self.open_batch_image(batch_reference_path))

    def open_batch_image(self,path):
        os.startfile(path) 