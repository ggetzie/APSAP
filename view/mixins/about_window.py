from PyQt5.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

class ImageWindow(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        main_view = self
        main_view.label = QLabel("This application is for education purposes only."  )
        layout.addWidget(main_view.label)
        main_view.setLayout(layout)

class AboutMixin:

    def showAbout(self):
        self.aboutWindow = ImageWindow()
        self.aboutWindow.show()
 