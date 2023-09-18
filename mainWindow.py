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
    print(f"main_model {time.time() - now} seconds have passed")
    now = time.time()
    main_view = MainView()
    print(f"main_view {time.time() - now} seconds have passed")
    now = time.time()
    main_presenter = Mainpresenter(main_model, main_view)
    print(f"main_presenter {time.time() - now} seconds have passed")
    now = time.time()
    main_view.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
