from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys

class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.root_path = "D:\\ararat\\data\\files\\N\\38\\478130\\4419430\\"
        self.context_folder =  Path(self.root_path).joinpath(str(context_number),'finds','3dbatch','2022')

        batch_list = []
        #double check folde exists 
        if not context_folder.exists():
            print("Batch has not finished building all the 3d models")
        else:
            batch_list = [batch for batch in context_folder.iterdir() if (batch.is_dir() and ('batch' in batch.stem) and not ('einscan' in batch.stem)) ] #read in all the files 

        self.batch_list_widget = QListWidget()

        for batch_name in batch_list:
            batch_list_widget.addItem(batch_name.stem)

        layout.addWidget(batch_name)
        


app = QApplication(sys.argv)
screen = Window()
screen.show()
sys.exit(app.exec_())