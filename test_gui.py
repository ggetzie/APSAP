import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QTableWidget, QTableWidgetItem
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5 import QtCore


class App(QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 layout - pythonspot.com'
        self.left = 500
        self.top = 100
        self.width = 800
        self.height = 800
        self.label_list = ["Age", 'Position']
        self.current_vial = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.vialGroupBox = self.createVialButtons()
        self.tableGroupBox = self.createTable()

        self.windowLayout = QVBoxLayout()
        self.windowLayout.addWidget(self.vialGroupBox)
        self.windowLayout.addWidget(self.tableGroupBox)
        self.setLayout(self.windowLayout)

        self.show()

    def createVialButtons(self):
        vialGroupBox = QGroupBox("Vials")
        layout = QGridLayout()
        for button_ind in range(100):
            row_ind = button_ind % 10
            col_ind = int(button_ind / 10)
            button = QPushButton('{} - {}'.format(row_ind + 1, col_ind + 1))
            button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            button.clicked.connect(self.show_info)
            layout.addWidget(button, row_ind, col_ind)
        vialGroupBox.setLayout(layout)
        return vialGroupBox

    def createTable(self):
        GroupBox = QGroupBox("Information")
        GroupBox.setMaximumHeight(110)
        self.table_layout = QHBoxLayout()
        self.tableWidget = QTableWidget()
        self.col_num = len(self.label_list) - 1
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(self.col_num)
        self.tableWidget.setHorizontalHeaderLabels(self.label_list)
        for cell_ind in range(self.col_num):
            item = QTableWidgetItem("")
            self.tableWidget.setItem(0, cell_ind, item)

        self.table_layout.addWidget(self.tableWidget)
        GroupBox.setLayout(self.table_layout)
        return GroupBox

    def refresh(self):
        # print('refresh')
        self.windowLayout.removeWidget(self.vialGroupBox)
        self.windowLayout.removeWidget(self.tableGroupBox)
        self.vialGroupBox = self.createVialButtons()
        self.tableGroupBox = self.createTable()
        self.windowLayout.addWidget(self.vialGroupBox)
        self.windowLayout.addWidget(self.tableGroupBox)


    def show_info(self):
        sending_button = self.sender()
        self.current_vial = sending_button.text()
        self.refresh()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())