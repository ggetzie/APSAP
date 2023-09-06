from PyQt5.QtWidgets import QApplication
from model.main_model import MainModel
from view.main_view import MainView
from presenter.main_presenter import Mainpresenter
import sys


def main():
    """Main function."""

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    import time
    now = time.time()
    
    main_model = MainModel()
    main_view = MainView()
    main_presenter = Mainpresenter(main_model, main_view)

    main_view.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
