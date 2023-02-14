from PyQt5.QtWidgets import QApplication
from model.main_model import MainModel
from view.main_view import MainView
from presenter.main_presenter import Mainpresenter
import sys
 
def main():
    """Main function."""
    # Create an instance of QApplication and setup the appropriate 
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    #Set up the data(model) and gui(view)
    main_model = MainModel()
    main_view = MainView()#main_model)  # presenter is initizilized inside mainWindow
    main_presenter = Mainpresenter(main_model, main_view)
    main_view.show()

    #leave the application after the gui application is closed
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
