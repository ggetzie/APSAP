import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import glob
import cv2
from sift_matching import *
from pathlib import *
from manual_match_widget import *
from auto_match_widget import *

# Create a subclass of QMainWindow to setup the calculator's GUI
class Main_Widget(QWidget):
    """View (GUI)."""
    def __init__(self):
        """View initializer."""
        super(Main_Widget,self).__init__()
        self.setWindowTitle('Sherd Match Assistance')
        self.resize(1100, 600)
        self.default_context = 43
        self.default_img = 1
        self.curr_context = self.default_context
        self.curr_img = self.default_img
        self.total_img_num = 0
        self.initUI()

    def initUI(self):       
        self.individual_folder_exists = True
        #set variables for context and piece informations 
        self.root_path = "D:\\ararat\\data\\files\\N\\38\\478130\\4419430\\"
        self.total_context_num = len([x for x in os.listdir(self.root_path) if x.isdigit()])
        
        self.curr_context_path = self.root_path + "{}\\finds\\individual\\".format(self.curr_context)
        if not os.path.isdir(self.curr_context_path):
            self.individual_folder_exists = False
        else:
            self.total_img_num = len([x for x in os.listdir(self.curr_context_path) if x.isdigit()])
            self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
       
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
        self.button_context_last.setText('last context')
        self.button_context_last.clicked.connect(self.last_context)

        self.button_context_next = QPushButton(self)
        self.button_context_next.setText('next context')
        self.button_context_next.clicked.connect(self.next_context)

        self.button_open_file_explorer = QPushButton(self)
        self.button_open_file_explorer.setText('open_context_folder')
        self.button_open_file_explorer.clicked.connect(self.open_file_explorer)

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
        self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))
    
        self.button_sherd_last = QPushButton(self)
        self.button_sherd_last.setText('last sherd')
        self.button_sherd_last.clicked.connect(self.last_sherd)

        self.button_sherd_next = QPushButton(self)
        self.button_sherd_next.setText('next sherd')
        self.button_sherd_next.clicked.connect(self.next_sherd)

        ############################ add elements ######################################
        if self.individual_folder_exists:
            self.set_images()

        ######### Build a Tab area for switching between manual and automatic matching ########## 
        self.tabwidget = QTabWidget()

        self.auto_match_section = auto_match_widget(self.curr_context_path,self.path_img_frt,self.path_img_back)
        self.tabwidget.addTab(manual_match_widget(self.root_path,self.curr_context), "manual matching")
        self.tabwidget.addTab(self.auto_match_section, "Auto matching")

        self.root_layout.addLayout(self.query_area_main_layout)

        self.query_area_main_layout.addLayout(self.context_info_layout)
        self.context_info_layout.addWidget(self.context_label)
        self.context_info_layout.addWidget(self.button_context_last)
        self.context_info_layout.addWidget(self.button_context_next)

        self.query_area_main_layout.addWidget(self.image_label)
        self.query_area_main_layout.addWidget(self.button_open_file_explorer)
        self.button_open_file_explorer.setVisible(False)
        self.query_area_main_layout.addWidget(self.query_img_frt_label)
        self.query_area_main_layout.addWidget(self.query_img_back_label)

        self.query_area_main_layout.addLayout(self.sherd_info_layout)
        self.sherd_info_layout.addWidget(self.sherd_label)
        self.sherd_info_layout.addWidget(self.button_sherd_last)
        self.sherd_info_layout.addWidget(self.button_sherd_next)
        self.query_area_main_layout.addStretch()

        self.root_layout.addWidget(self.tabwidget)
        self.setLayout(self.root_layout)
        
    #mode==1 indicats folder missing, mode == 2 indicates image missing
    def clear_qury_area(self, mode):
        if mode == 1:
            self.image_label.setText("Current context does not contain the folder for indvidual.\nCheck in the File Explorer and contact admin for more information")
            self.query_img_frt_label.setVisible(False)
            self.query_img_back_label.setVisible(False)
            self.sherd_label.setVisible(False)
            self.button_sherd_last.setVisible(False)
            self.button_sherd_next.setVisible(False)
            self.button_open_file_explorer.setVisible(True)
        if mode == 2:
            self.image_label.setText("Current context does not contain the front and back individual photos\nCheck in the File Explorer and contact admin for more information")
            self.query_img_frt_label.setVisible(False)
            self.query_img_back_label.setVisible(False)
            self.button_open_file_explorer.setVisible(True)
        

    #mode==1 indicats folder missing, mode == 2 indicates image missing   
    def repopulate_qury_area(self):
        self.image_label.setText("Which sherd is this?")
        self.query_img_frt_label.setVisible(True)
        self.query_img_back_label.setVisible(True)
        self.sherd_label.setVisible(True)
        self.button_sherd_last.setVisible(True)
        self.button_sherd_next.setVisible(True)
        self.button_open_file_explorer.setVisible(False)
    
    def set_images(self):
        
        self.path_img_frt = self.path_curr_img + '\\1.jpg'
        self.path_img_back = self.path_curr_img + '\\2.jpg'
        self.myimage = QImage(self.path_img_frt)
        if self.myimage.isNull():
            self.clear_qury_area(mode=2)
            return
        self.query_img_frt_label.setPixmap(QPixmap.fromImage(self.myimage).scaledToHeight(300))
        self.query_img_frt_label.mousePressEvent = (lambda x: self.open_image(self.path_curr_img + "\\1.tif"))

        self.myimage = QImage(self.path_img_back)
        if self.myimage.isNull():
            self.clear_qury_area(mode=2)
            return
        self.query_img_back_label.setPixmap(QPixmap.fromImage(self.myimage).scaledToHeight(300))
        self.query_img_back_label.mousePressEvent = (lambda x: self.open_image(self.path_curr_img + "\\2.tif"))
        self.repopulate_qury_area()

    def update_auto_match_section(self, auto_match_section):
        auto_match_section.curr_context_path = self.curr_context_path
        auto_match_section.path_img_frt = self.path_img_frt
        auto_match_section.path_img_back = self.path_img_back

    def next_context(self):
        if (self.curr_context == self.total_context_num):
            pass
        else:
            self.curr_context +=1
            self.context_label.setText("Context number: {}".format(self.curr_context))
            self.curr_img = 1
            self.curr_context_path = self.root_path + "{}\\finds\\individual\\".format(self.curr_context)

            if not os.path.isdir(self.curr_context_path):
                self.clear_qury_area(mode=1)
            else:
                self.image_label.setText("Which sherd is this?")
                self.total_img_num = len([x for x in os.listdir(self.curr_context_path) if x.isdigit()])
                self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
                self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))
                self.set_images()
            
            self.update_auto_match_section(self.auto_match_section)
            self.tabwidget.removeTab(0)
            self.tabwidget.insertTab(0, manual_match_widget(self.root_path,self.curr_context), "manual matching" )
            self.tabwidget.setCurrentIndex(0)

    def last_context(self):
        if (self.curr_context == 1):
            pass
        else:
            self.curr_context -=1
            self.context_label.setText("Context number: {}".format(self.curr_context))
            self.curr_img = 1
            self.curr_context_path = self.root_path + "{}\\finds\\individual\\".format(self.curr_context)
            
            if not os.path.isdir(self.curr_context_path):
                self.clear_qury_area(mode=1)
            else:
                self.image_label.setText("Which sherd is this?")
                self.total_img_num = len([x for x in os.listdir(self.curr_context_path) if x.isdigit()])
                self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
                self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))
                self.set_images()
            
            self.update_auto_match_section(self.auto_match_section)
            self.tabwidget.removeTab(0)
            self.tabwidget.insertTab(0, manual_match_widget(self.root_path,self.curr_context), "manual matching" )
            self.tabwidget.setCurrentIndex(0)

    def next_sherd(self):
        if (self.curr_img == self.total_img_num):
            pass
        else:
            self.curr_img +=1
            self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
            self.set_images()
            self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))
            self.update_auto_match_section(self.auto_match_section)

    def last_sherd(self):
        if (self.curr_img == 1):
            pass
        else:
            self.curr_img -=1
            self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
            self.set_images()
            self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))
            self.update_auto_match_section(self.auto_match_section)

    #open image in default program
    def open_image(self, image_to_open):
        os.startfile(image_to_open) 

    def open_file_explorer(self):
        os.startfile(self.root_path + str(self.curr_context))

def main():
    """Main function."""
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    # Show the calculator's GUI
    main = Main_Widget()
    main.show()
    # Execute the calculator's main loop
    sys.exit(app.exec_())

   
if __name__ == '__main__':
   main()