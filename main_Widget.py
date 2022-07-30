import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import glob
import cv2
from sift_matching import *
from pathlib import *

# Create a subclass of QMainWindow to setup the calculator's GUI
class Main_Widget(QWidget):
    """View (GUI)."""
    def __init__(self):
        """View initializer."""
        super(Main_Widget,self).__init__()
        self.setWindowTitle('Sherd Match Assistance')
        self.resize(1000, 600)
        self.default_context = 43
        self.default_img = 1
        self.curr_context = self.default_context
        self.curr_img = self.default_img
        self.initUI()

    def initUI(self):       
    
        self.root_path = "D:\\ararat\\data\\files\\N\\38\\478130\\4419430\\"
        self.total_context_num = len([x for x in os.listdir(self.root_path) if x.isdigit()])
        
        self.curr_context_path = self.root_path + "{}\\finds\\individual\\".format(self.curr_context)
        self.total_img_num = len([x for x in os.listdir(self.curr_context_path) if x.isdigit()])
        self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
       
        # Root Layer
        self.root_layout = QHBoxLayout()
        ## 2 Layer ##
        self.query_area_main_layout = QVBoxLayout()
        self.prediction_area_layout = QVBoxLayout()
        
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

        self.image_label = QLabel(self)
        self.image_label.setText("Which sherd is this?")
        self.image_label.setAlignment(Qt.AlignTop)
        self.image_label.setFixedHeight(20)

        ###################### Widgets for query image ##################################

        self.query_img_frt_label = QLabel(self)
        self.query_img_back_label = QLabel(self)
        
        self.set_images()

        ########################## Widgets for sherd info ################################
        self.sherd_label = QLabel(self)
        self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))
    
        self.button_sherd_last = QPushButton(self)
        self.button_sherd_last.setText('last sherd')
        self.button_sherd_last.clicked.connect(self.last_sherd)

        self.button_sherd_next = QPushButton(self)
        self.button_sherd_next.setText('next sherd')
        self.button_sherd_next.clicked.connect(self.next_sherd)

        ########################### Automatic matching button ###################################
        self.button_find = QPushButton(self)
        self.button_find.setText('find')
        self.button_find.clicked.connect(self.activate_model)

        ############# Header label for prediction display area ##############
        self.label_candidates_list = QLabel(self)
        self.label_candidates_list.setAlignment(Qt.AlignTop)
        self.label_candidates_list.setText("Candidate matches:")
        self.label_candidates_list.setFixedHeight(20)

        ################### Build a Scrollable Area to display candidates ##########################
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        
        self.groupBox = QGroupBox()
        self.scroll_area_layout = QFormLayout()
        self.groupBox.setLayout(self.scroll_area_layout)
        self.scroll.setWidget(self.groupBox)

        #add elements
        self.root_layout.addLayout(self.query_area_main_layout)
        #root_layout.addStretch()
        self.root_layout.addLayout(self.prediction_area_layout)

        self.query_area_main_layout.addLayout(self.context_info_layout)
        self.context_info_layout.addWidget(self.context_label)
        self.context_info_layout.addWidget(self.button_context_last)
        self.context_info_layout.addWidget(self.button_context_next)

        self.query_area_main_layout.addWidget(self.image_label)
        self.query_area_main_layout.addWidget(self.query_img_frt_label)
        self.query_area_main_layout.addWidget(self.query_img_back_label)

        self.query_area_main_layout.addLayout(self.sherd_info_layout)
        self.sherd_info_layout.addWidget(self.sherd_label)
        self.sherd_info_layout.addWidget(self.button_sherd_last)
        self.sherd_info_layout.addWidget(self.button_sherd_next)

        self.query_area_main_layout.addWidget(self.button_find)
        self.query_area_main_layout.addStretch()

        self.prediction_area_layout.addWidget(self.label_candidates_list)
        self.prediction_area_layout.addWidget(self.scroll)
        
        self.setLayout(self.root_layout)

    def set_images(self):
                self.path_img_frt = self.path_curr_img + '\\1.jpg'
                self.path_img_back = self.path_curr_img + '\\2.jpg'
                
                self.myimage = QImage(self.path_img_frt)
                if self.myimage.isNull():
                    QMessageBox.information(self, "Image Viewer",
                            "Cannot load %s." % self.path_img_frt)
                    return
                self.query_img_frt_label.setPixmap(QPixmap.fromImage(self.myimage).scaledToHeight(300))
                self.query_img_frt_label.mousePressEvent = (lambda x: self.open_image(self.path_curr_img + "\\1.tif"))

                self.myimage = QImage(self.path_img_back)
                if self.myimage.isNull():
                    QMessageBox.information(self, "Image Viewer",
                            "Cannot load %s." % self.path_img_back)
                    return
                self.query_img_back_label.setPixmap(QPixmap.fromImage(self.myimage).scaledToHeight(300))
                self.query_img_back_label.mousePressEvent = (lambda x: self.open_image(self.path_curr_img + "\\2.tif"))

    def next_context(self):
        if (self.curr_context == self.total_context_num):
            pass
        else:
            for i in reversed(range(self.scroll_area_layout.count())): 
                widgetToRemove = self.scroll_area_layout.itemAt(i).widget()
                # remove it from the layout list
                self.scroll_area_layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)

            self.curr_context +=1
            self.context_label.setText("Context number: {}".format(self.curr_context))
            self.curr_img = 1
            self.curr_context_path = self.root_path + "{}\\finds\\individual\\".format(self.curr_context)
            self.total_img_num = len([x for x in os.listdir(self.curr_context_path) if x.isdigit()])
            self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
            self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))
            self.set_images()

    def last_context(self):
        if (self.curr_context == 1):
            pass
        else:
            for i in reversed(range(self.scroll_area_layout.count())): 
                widgetToRemove = self.scroll_area_layout.itemAt(i).widget()
                # remove it from the layout list
                self.scroll_area_layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)
            
            self.curr_context -=1
            self.context_label.setText("Context number: {}".format(self.curr_context))
            self.curr_img = 1
            self.curr_context_path = self.root_path + "{}\\finds\\individual\\".format(self.curr_context)
            self.total_img_num = len([x for x in os.listdir(self.curr_context_path) if x.isdigit()])
            self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
            self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))
            self.set_images()

    def next_sherd(self):
        if (self.curr_img == self.total_img_num):
            pass
        else:
            for i in reversed(range(self.scroll_area_layout.count())): 
                widgetToRemove = self.scroll_area_layout.itemAt(i).widget()
                # remove it from the layout list
                self.scroll_area_layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)

            self.curr_img +=1
            self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
            self.set_images()
            self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))


    def last_sherd(self):
        if (self.curr_img == 1):
            pass
        else:
            for i in reversed(range(self.scroll_area_layout.count())): 
                widgetToRemove = self.scroll_area_layout.itemAt(i).widget()
                # remove it from the layout list
                self.scroll_area_layout.removeWidget(widgetToRemove)
                # remove it from the gui
                widgetToRemove.setParent(None)

            self.curr_img -=1
            self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
            self.set_images()
            self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))

    #open image in default program
    def open_image(self, image_to_open):
        os.startfile(image_to_open) 
    


    #call predicting model 
    def activate_model(self):
        
        #if the 2d target images have been created in the context
        batch_list = [batch for batch in Path(self.curr_context_path).iterdir() if (batch.is_dir() and ('batch' in batch.stem) and ('einscan' not in batch.stem)) ] #read in all the files 
        proceed = True

        for one_batch in batch_list:
            target_images_folder = one_batch.joinpath('registration_reso1_maskthres242','final_output','individual_images')

            if not target_images_folder.exists():
                    print("Batch has not finished building all the 3d models") #TODO
                    proceed = False
                    break
            else:
                piece_model_list = [file for file in target_images_folder.parent.iterdir() if file.suffix == '.ply'] #read in all the files 
                piece_model_pcd_list = [ file for file in piece_model_list if file.stem[-1] == 'd']  #keep only the first pointclouds, modify as needed

                #check having read in the correct number of ply file
                if (len(piece_model_pcd_list) == 0) or (len(piece_model_list) % 3 != 0):
                    print("number of ply file is not correct") #TODO
                    proceed = False
                    break
                else:                    
                    target_images_list = [file for file in target_images_folder.rglob('*') if file.suffix == '.png']

                    if (len(target_images_list) != 2*len(piece_model_pcd_list)):
                        print("number of target images is not correct") #TODO
                        proceed = False
                        break 

        if proceed:

            all_targets_for_context_list = read_context_targets(Path(self.curr_context_path))

            query_img_frt = cv2.imread(self.path_img_frt)
            query_img_back = cv2.imread(self.path_img_back)

            sorted_target_list = []

            for one_target in all_targets_for_context_list:

                target_img_front = cv2.imread(one_target[1])
                target_img_back = cv2.imread(one_target[2])

                good_match_num = img_compare(query_img_frt, target_img_front) + img_compare(query_img_back, target_img_back)

                target_img_batch_num = int(((one_target[1]).parts[-6])[-3::])
                
                target_img_num = int((one_target[1]).parts[-2])

                sorted_target_list.append((good_match_num, target_img_num, target_img_batch_num, one_target[1], one_target[2]))

            sorted_target_list.sort(key=lambda x: x[0],reverse=True)

            for sorted_target in sorted_target_list:

                self.candidate_img_frt = QLabel(self)
                self.candidate_img_frt.setPixmap(QPixmap(sorted_target[-2]).scaledToHeight(150))
                #self.candidate_img_frt.setAlignment(Qt.AlignTop | Qt.AlignLeft)

                self.candidate_img_back = QLabel(self)
                self.candidate_img_back.setPixmap(QPixmap(sorted_target[-1]).scaledToHeight(150))
                #self.candidate_img_back.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                
                self.candidate_card_layout = QVBoxLayout()
                self.candidate_card_images_layout = QHBoxLayout()
                self.candidate_card_labels_layout = QHBoxLayout()
                
                self.candidate_batch_label = QLabel(self)
                self.candidate_batch_label.setText("Batch Number:")
                #self.candidate_batch_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                self.candidate_batch_label.setFixedHeight(30)

                self.candidate_piece_label = QLabel(self)
                self.candidate_piece_label.setText("Piece number:")
                #self.candidate_piece_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                self.candidate_piece_label.setFixedHeight(30)


                self.match_points_label = QLabel(self)
                self.match_points_label.setText("match points:")
                #self.match_points_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                self.match_points_label.setFixedHeight(30)

                self.candidate_card_images_layout.addWidget(self.candidate_img_frt)
                self.candidate_card_images_layout.addWidget(self.candidate_img_back)
                self.candidate_card_labels_layout.addWidget(self.candidate_batch_label)
                self.candidate_card_labels_layout.addWidget(self.candidate_piece_label)
                self.candidate_card_labels_layout.addWidget(self.match_points_label)

                self.candidate_card_layout.addLayout(self.candidate_card_images_layout)
                self.candidate_card_layout.addLayout(self.candidate_card_labels_layout)
                
                self.scroll_area_layout.addRow(self.candidate_card_layout)
            
            self.groupBox.setLayout(self.scroll_area_layout)


def main():
    """Main function."""
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    # Show the calculator's GUI
    #main = QMainWindow()
    main = Main_Widget()
    main.show()
    # Execute the calculator's main loop
    sys.exit(app.exec_())

   
if __name__ == '__main__':
   main()