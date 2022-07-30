import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import glob

# Create a subclass of QMainWindow to setup the calculator's GUI
class Main_Widget(QWidget):
    """View (GUI)."""
    def __init__(self):
        """View initializer."""
        super(Main_Widget,self).__init__()
        self.setWindowTitle('Sherd Match Assistance')
        self.resize(1000, 600)
        self.default_context = 38
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

        self.query_image_frt = QLabel(self)
        self.query_image_back = QLabel(self)
        
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
        
        ############## Populate temporarily the scrollable for testing purpose######################
        self.scroll_area_layout = QFormLayout()
        self.groupBox = QGroupBox()
        self.my_path = os.path.dirname(os.path.abspath(__file__))
        self.data_folder =  os.path.dirname(self.my_path) + '\\context 41\\batch_000\\data_set'

        self.files = glob.glob(self.data_folder + '/**/*.jpg', recursive=True)

        for file in self.files:

            self.candidate_image = QLabel(self)
            self.myimage = QImage(file)
            self.candidate_image.setPixmap(QPixmap.fromImage(self.myimage))
            self.candidate_image.setFixedSize(300, 200)
            self.candidate_image.setAlignment(Qt.AlignTop | Qt.AlignLeft)

            self.candidate_card_layout = QHBoxLayout()
            self.candidate_card_labels_layout = QVBoxLayout()

            self.candidate_batch_label = QLabel(self)
            self.candidate_batch_label.setText("Batch Number:")
            self.candidate_batch_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.candidate_batch_label.setFixedHeight(30)

            self.candidate_piece_label = QLabel(self)
            self.candidate_piece_label.setText("Piece number:")
            self.candidate_piece_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.candidate_piece_label.setFixedHeight(30)


            self.candidate_prob_label = QLabel(self)
            self.candidate_prob_label.setText("Probability:")
            self.candidate_prob_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.candidate_prob_label.setFixedHeight(30)


            self.candidate_card_layout.addWidget(self.candidate_image)
            self.candidate_card_layout.addLayout(self.candidate_card_labels_layout)
            self.candidate_card_labels_layout.addWidget(self.candidate_batch_label)
            self.candidate_card_labels_layout.addWidget(self.candidate_piece_label)
            self.candidate_card_labels_layout.addWidget(self.candidate_prob_label)
            
            self.scroll_area_layout.addRow(self.candidate_card_layout)
    

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
        self.query_area_main_layout.addWidget(self.query_image_frt)
        self.query_area_main_layout.addWidget(self.query_image_back)

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
                self.query_image_frt.setPixmap(QPixmap.fromImage(self.myimage).scaledToHeight(300))
                self.query_image_frt.mousePressEvent = (lambda x: self.open_image(self.path_curr_img + "\\1.tif"))

                self.myimage = QImage(self.path_img_back)
                if self.myimage.isNull():
                    QMessageBox.information(self, "Image Viewer",
                            "Cannot load %s." % self.path_img_back)
                    return
                self.query_image_back.setPixmap(QPixmap.fromImage(self.myimage).scaledToHeight(300))
                self.query_image_back.mousePressEvent = (lambda x: self.open_image(self.path_curr_img + "\\2.tif"))

    def next_context(self):
        if (self.curr_context == self.total_context_num):
            pass
        else:
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
            self.curr_img +=1
            self.path_curr_img = self.curr_context_path + "{}\\photos".format(self.curr_img)
            self.set_images()
            self.sherd_label.setText("Sherd number: {} out of {}".format(self.curr_img, self.total_img_num))


    def last_sherd(self):
        if (self.curr_img == 1):
            pass
        else:
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
        batch_list = [batch for batch in self.curr_context_path.iterdir() if (batch.is_dir() and ('batch' in batch.stem) and ('einscan' not in batch.stem)) ] #read in all the files 
        proceed = True

        for one_batch in batch_list:
            target_images_folder = one_batch.joinpath('registration_reso1_maskthres242','final_output','individual_images')

            if not target_images_folder.exists():
                    print("Batch has not finished building all the 3d models") #TODO
                    proceed = False
                    break
                else:
                    piece_model_list = [file for file in models_folder.iterdir() if file.suffix == '.ply'] #read in all the files 
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


            all_targets_for_context_list = read_context_targets(self.curr_context_path)

            

    #read in all target match files in one list of tuples in (front_path, back_path) format         
    def read_context_targets(target_context_path):    
        context_front_list =  [file for file in target_context_path.rglob('*') if file.name == '2d_image_front.png']
        context_back_list =  [file for file in target_context_path.rglob('*') if file.name == '2d_image_front.png']
        
        master_context_targets_space = []

        if len(context_front_list) != len(context_back_list):
            print("the number of front and back target images is not consistent")
        else:
            
            for i in len(context_front_list)
                master_context_targets_space.append((context_front_list[i],context_back_list[1]))

        return master_context_targets_space



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