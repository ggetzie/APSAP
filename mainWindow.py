from PyQt5.QtWidgets import QApplication
from model.mainModel import MainModel
from view.mainView import MainView
 
import sys
 
def main():
    """Main function."""
    # Create an instance of QApplication and setup the appropriate 
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    #Set up the data(model) and gui(view)
    mainModel = MainModel()
    mainView = MainView(mainModel)  # Controller is initizilized inside mainWindow
    mainView.show()

    #leave the application after the gui application is closed
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
