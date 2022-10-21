import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QTabWidget,
    QGroupBox,
    QComboBox,
    QTextEdit,
)
import os
import pathlib
from manual_match_widget import *
from auto_match_widget import *
from database_tools import get_pottery_sherd_info, update_match_info

basedir = os.path.dirname(os.path.realpath(__file__))
# FILE_ROOT = pathlib.Path("D:\\ararat\\data\\files")
FILE_ROOT = pathlib.Path(
    "C:\\Users\\gabe\\OneDrive - The University Of Hong Kong\\HKU\\02-Projects\\P22007-Cobb_ArchaeologyData\\Ceramics Matching\\sample"
)
HEMISPHERES = ("N", "S")
# Create a subclass of QMainWindow to setup the calculator's GUI
class Main_Widget(QWidget):
    """View (GUI)."""

    def __init__(self):
        """View initializer."""
        super(Main_Widget, self).__init__()
        self.setWindowTitle("Sherd Match Assistance")
        self.setWindowIcon(QIcon(os.path.join(basedir, "assets", "icon.png")))
        self.resize(1100, 600)
        self.default_hemisphere = "N"
        self.default_zone = 38
        # self.default_trench = (478130, 4419430)  # (utm_easting, utm_northing)
        self.default_trench = (478020, 4419550)  # (utm_easting, utm_northing)
        # self.default_context = 42
        self.default_context = 11
        self.default_img = 1
        self.curr_trench = self.default_trench
        self.curr_context = self.default_context
        self.curr_img = self.default_img
        self.total_img_num = 0
        self.initUI()

    def initUI(self):
        self.individual_folder_exists = True
        # set variables for context and piece information
        # self.root_path = "D:\\ararat\\data\\files\\N\\38\\{}\\{}\\".format(
        #     self.curr_trench[0], self.curr_trench[1]
        # )
        self.root_path = (
            FILE_ROOT
            / self.default_hemisphere
            / str(self.default_zone)
            / str(self.curr_trench[0])
            / str(self.curr_trench[1])
        )
        self.total_context_list = [
            int(x) for x in os.listdir(self.root_path) if x.isdigit()
        ]

        self.total_context_list.sort()
        self.total_context_list = [str(x) for x in self.total_context_list]
        self.total_context_num = len(self.total_context_list)

        self.cur_context_individual_path = (
            self.root_path / str(self.curr_context) / "finds/individual"
        )
        self.cur_context_3dbatch_path = (
            self.root_path / str(self.curr_context) / "finds/3dbatch/2022"
        )
        if not self.cur_context_individual_path.is_dir():
            self.individual_folder_exists = False
            print(f"{self.cur_context_individual_path} does not exist")
        else:
            self.total_img_list = [
                int(x)
                for x in os.listdir(self.cur_context_individual_path)
                if x.isdigit()
            ]
            self.total_img_list.sort()
            self.total_img_list = [str(x) for x in self.total_img_list]
            self.total_img_num = len(self.total_img_list)
            self.path_curr_img = (
                self.cur_context_individual_path / str(self.curr_img) / "photos"
            )

        # Root Layer
        self.root_layout = QHBoxLayout()
        ## 2 Layer ##
        self.query_area_main_layout = QVBoxLayout()

        ## 3 Layer ##
        self.context_info_layout = QHBoxLayout()
        self.sherd_info_layout = QHBoxLayout()

        ###################### Widgets for Context info #################################
        self.context_label = QLabel(self)
        self.context_label.setText("Context number: {}".format(self.curr_context))

        self.button_context_last = QPushButton(self)
        self.button_context_last.setText("last context")
        self.button_context_last.clicked.connect(
            (lambda x: self.change_context(self.curr_context - 1))
        )

        self.button_context_next = QPushButton(self)
        self.button_context_next.setText("next context")
        self.button_context_next.clicked.connect(
            (lambda x: self.change_context(self.curr_context + 1))
        )

        self.button_open_file_explorer = QPushButton(self)
        self.button_open_file_explorer.setText("open_context_folder")
        self.button_open_file_explorer.clicked.connect(self.open_file_explorer)

        ### add combobox to jump to designated context
        self.context_combobox = QComboBox()
        self.populate_context_combobox()
        self.context_combobox.currentTextChanged.connect(self.change_context)

        self.image_label = QLabel(self)
        self.image_label.setText("Which sherd is this?")
        self.image_label.setAlignment(Qt.AlignTop)
        self.image_label.setFixedHeight(40)

        ###################### Widgets for query image ##################################
        self.query_img_frt_label = QLabel(self)
        self.query_img_back_label = QLabel(self)

        self.query_img_frt_label.setVisible(False)
        self.query_img_back_label.setVisible(False)

        ########################## Widgets for sherd info ################################
        self.sherd_label = QLabel(self)
        self.sherd_label.setText(
            "Sherd number: {} out of {}".format(self.curr_img, self.total_img_num)
        )

        self.button_sherd_last = QPushButton(self)
        self.button_sherd_last.setText("last sherd")
        self.button_sherd_last.clicked.connect(
            (lambda x: self.change_sherd(self.curr_img - 1))
        )

        self.button_sherd_next = QPushButton(self)
        self.button_sherd_next.setText("next sherd")
        self.button_sherd_next.clicked.connect(
            (lambda x: self.change_sherd(self.curr_img + 1))
        )

        self.sherd_combobox = QComboBox()
        self.populate_sherd_combobox()
        self.sherd_combobox.currentTextChanged.connect(self.change_sherd)

        ########################## Widgets for manual matching input ###################

        self.match_input = QGroupBox()
        self.match_input.setTitle("Input Matching info")
        self.match_input_layout = QHBoxLayout()
        self.match_input.setLayout(self.match_input_layout)
        self.batch_label = QLabel()
        self.batch_label.setText("Batch Number")
        self.batch_input = QTextEdit()
        self.batch_input.setFixedHeight(30)
        self.piece_label = QLabel()
        self.piece_label.setText("Sherd Number")
        self.sherd_input = QTextEdit()
        self.sherd_input.setFixedHeight(30)

        self.update_batch_info()

        self.button_confirm = QPushButton(self)
        self.button_confirm.setText("confirm selection")
        self.button_confirm.clicked.connect(self.show_confirm_dialog)

        if self.individual_folder_exists:
            self.set_images()

        ######### Build a Tab area for switching between manual and automatic matching ##########
        self.tabwidget = QTabWidget()

        self.suggested_batches = identify_range_of_batches(
            self.curr_trench[0],
            self.curr_trench[1],
            str(self.curr_context),
            str(self.curr_img),
        )
        # print(self.suggested_batches)
        self.auto_match_section = auto_match_widget(self)
        self.manual_match_section = manual_match_widget(self)
        self.tabwidget.addTab(self.manual_match_section, "manual matching")
        self.tabwidget.addTab(self.auto_match_section, "Auto matching")

        ############################ add elements ######################################
        self.root_layout.addLayout(self.query_area_main_layout)

        self.query_area_main_layout.addLayout(self.context_info_layout)
        self.context_info_layout.addWidget(self.context_label)
        self.context_info_layout.addWidget(self.button_context_last)
        self.context_info_layout.addWidget(self.button_context_next)
        self.context_info_layout.addWidget(self.context_combobox)

        self.query_area_main_layout.addWidget(self.image_label)
        self.query_area_main_layout.addWidget(self.button_open_file_explorer)
        self.button_open_file_explorer.setVisible(False)
        self.query_area_main_layout.addWidget(self.query_img_frt_label)
        self.query_area_main_layout.addWidget(self.query_img_back_label)

        self.query_area_main_layout.addLayout(self.sherd_info_layout)
        self.sherd_info_layout.addWidget(self.sherd_label)
        self.sherd_info_layout.addWidget(self.button_sherd_last)
        self.sherd_info_layout.addWidget(self.button_sherd_next)
        self.sherd_info_layout.addWidget(self.sherd_combobox)

        self.query_area_main_layout.addWidget(self.match_input)
        self.match_input_layout.addWidget(self.batch_label)
        self.match_input_layout.addWidget(self.batch_input)
        self.match_input_layout.addWidget(self.piece_label)
        self.match_input_layout.addWidget(self.sherd_input)
        self.match_input_layout.addWidget(self.button_confirm)

        self.query_area_main_layout.addStretch()

        self.root_layout.addWidget(self.tabwidget)
        self.setLayout(self.root_layout)

    def update_batch_info(self):
        batch_num, sherd_num = get_pottery_sherd_info(
            self.curr_trench[0], self.curr_trench[1], self.curr_context, self.curr_img
        )
        if batch_num != None and sherd_num != None:
            self.batch_input.setText(str(batch_num))
            self.sherd_input.setText(str(sherd_num))
        else:
            self.batch_input.clear()
            self.sherd_input.clear()

    def populate_context_combobox(self):
        self.context_combobox.clear()
        self.context_combobox.addItems(self.total_context_list)
        self.context_combobox.setCurrentIndex(self.curr_context - 1)

    def populate_sherd_combobox(self):
        self.sherd_combobox.clear()
        self.sherd_combobox.addItems(self.total_img_list)
        self.sherd_combobox.setCurrentIndex(self.curr_img - 1)

    # mode==1 indicates folder missing, mode == 2 indicates image missing
    def clear_qury_area(self, mode):
        self.query_img_frt_label.setVisible(False)
        self.query_img_back_label.setVisible(False)
        self.button_open_file_explorer.setVisible(True)
        self.match_input.setVisible(False)
        if mode == 1:
            self.image_label.setText(
                "Current context does not contain the folder for individual.\nCheck in the File Explorer and contact admin for more information"
            )
            self.sherd_label.setVisible(False)
            self.button_sherd_last.setVisible(False)
            self.button_sherd_next.setVisible(False)
        if mode == 2:
            self.image_label.setText(
                "Current context does not contain the front and back individual photos\nCheck in the File Explorer and contact admin for more information"
            )

    # mode==1 indicates folder missing, mode == 2 indicates image missing
    def repopulate_query_area(self):
        self.image_label.setText("Which sherd is this?")
        self.query_img_frt_label.setVisible(True)
        self.query_img_back_label.setVisible(True)
        self.sherd_label.setVisible(True)
        self.button_sherd_last.setVisible(True)
        self.button_sherd_next.setVisible(True)
        self.button_open_file_explorer.setVisible(False)
        self.match_input.setVisible(True)

    def set_images(self):
        self.path_img_frt = self.path_curr_img / "1.jpg"
        self.path_img_back = self.path_curr_img / "2.jpg"
        self.myimage = QImage(str(self.path_img_frt))
        if self.myimage.isNull():
            self.clear_qury_area(mode=2)
            return
        self.query_img_frt_label.setPixmap(
            QPixmap.fromImage(self.myimage).scaledToHeight(300)
        )
        self.query_img_frt_label.mousePressEvent = lambda x: self.open_image(
            self.path_curr_img / "1.tif"
        )

        self.myimage = QImage(str(self.path_img_back))
        if self.myimage.isNull():
            self.clear_qury_area(mode=2)
            return
        self.query_img_back_label.setPixmap(
            QPixmap.fromImage(self.myimage).scaledToHeight(300)
        )
        self.query_img_back_label.mousePressEvent = lambda x: self.open_image(
            self.path_curr_img / "2.tif"
        )
        self.repopulate_query_area()

    def change_context(self, new_context):
        new_context = int(new_context)
        if (new_context > self.total_context_num) or (new_context < 1):
            pass
        else:
            self.context_combobox.setCurrentIndex(new_context - 1)
            self.curr_context = new_context
            self.context_label.setText("Context number: {}".format(self.curr_context))
            self.curr_img = 1
            self.cur_context_individual_path = (
                self.root_path + "{}\\finds\\individual\\".format(self.curr_context)
            )
            self.cur_context_3dbatch_path = (
                self.root_path + "{}\\finds\\3dbatch\\2022\\".format(self.curr_context)
            )

            if not os.path.isdir(self.cur_context_individual_path):
                self.clear_qury_area(mode=1)
            else:
                self.image_label.setText("Which sherd is this?")
                self.total_img_list = [
                    int(x)
                    for x in os.listdir(self.cur_context_individual_path)
                    if x.isdigit()
                ]
                self.total_img_list.sort()
                self.total_img_list = [str(x) for x in self.total_img_list]
                self.total_img_num = len(self.total_img_list)
                self.path_curr_img = (
                    self.cur_context_individual_path
                    + "{}\\photos".format(self.curr_img)
                )
                self.sherd_label.setText(
                    "Sherd number: {} out of {}".format(
                        self.curr_img, self.total_img_num
                    )
                )
                self.sherd_combobox.currentTextChanged.disconnect()
                self.populate_sherd_combobox()
                self.sherd_combobox.currentTextChanged.connect(self.change_sherd)
                # self.sherd_combobox.clear()
                # self.sherd_combobox.addItems(self.total_img_list)
                self.set_images()

            self.update_batch_info()
            self.suggested_batches = identify_range_of_batches(
                self.curr_trench[0],
                self.curr_trench[1],
                str(self.curr_context),
                str(self.curr_img),
            )
            self.manual_match_section = manual_match_widget(self)
            self.tabwidget.removeTab(0)
            self.tabwidget.insertTab(0, self.manual_match_section, "manual matching")
            self.tabwidget.setCurrentIndex(0)

    def change_sherd(self, new_sherd):
        new_sherd = int(new_sherd)
        if (new_sherd > self.total_img_num) or (new_sherd < 1):
            pass
        else:
            self.sherd_combobox.setCurrentIndex(new_sherd - 1)
            self.curr_img = new_sherd
            self.path_curr_img = (
                self.cur_context_individual_path / "photos" / self.curr_img
            )
            self.set_images()
            self.sherd_label.setText(
                "Sherd number: {} out of {}".format(self.curr_img, self.total_img_num)
            )
            # self.update_auto_match_section(self.auto_match_section)
            self.suggested_batches = identify_range_of_batches(
                self.curr_trench[0],
                self.curr_trench[1],
                str(self.curr_context),
                str(self.curr_img),
            )
            self.manual_match_section = manual_match_widget(self)
            self.tabwidget.removeTab(0)
            self.tabwidget.insertTab(0, self.manual_match_section, "manual matching")
            self.tabwidget.setCurrentIndex(0)
            self.update_batch_info()

    # open image in default program
    def open_image(self, image_to_open):
        os.startfile(image_to_open)

    def open_file_explorer(self):
        os.startfile(self.root_path + str(self.curr_context))

    def update_database(self):
        new_batch_num = self.batch_input.toPlainText()
        new_sherd_num = self.sherd_input.toPlainText()
        update_match_info(
            self.curr_trench[0],
            self.curr_trench[1],
            self.curr_context,
            self.curr_img,
            new_batch_num,
            new_sherd_num,
        )

    def show_confirm_dialog(self):
        new_batch_num = self.batch_input.toPlainText()
        new_sherd_num = self.sherd_input.toPlainText()

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Confirm Your Selction")

        if (new_batch_num == "") or (new_sherd_num == ""):
            msgBox.setText("Input fields cannot be empty")
        elif (not new_batch_num.isdigit()) or (not new_sherd_num.isdigit()):
            msgBox.setText("Both inputs need to be numbers")
        else:
            msgBox.setText("Confirm your match?")
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.buttonClicked.connect(self.update_database)
        msgBox.exec()


def main():
    """Main function."""
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # Show the calculator's GUI
    main = Main_Widget()
    main.show()
    # Execute the calculator's main loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
