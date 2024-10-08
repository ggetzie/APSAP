from PyQt5.QtWidgets import QApplication
from model.main_model import MainModel
from view.main_view import MainView
from presenter.main_presenter import Mainpresenter
import sys
import logging
import time
from pathlib import Path
import getpass
from time import ctime

def main():
    """Main function."""

    #Setting the logger and logging file, and make sure logging information goes to both the file and 
    logFolder = f"./logs/{getpass.getuser()}"
    logPath = f"{logFolder}/{ctime().replace(':','')}.txt"
    Path(logFolder).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(logPath), logging.StreamHandler()],
    )

    #Setting the basic style
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    #Run the model, view and presenter one by one and count the time it takes to load each of them.
    now = time.time()
    main_model = MainModel()
    logging.info(f"main_model {time.time() - now} seconds have passed")
    now = time.time()
    main_view = MainView()
    logging.info(f"main_view {time.time() - now} seconds have passed")
    now = time.time()
    main_presenter = Mainpresenter(main_model, main_view)
    logging.info(f"main_presenter {time.time() - now} seconds have passed")
    logging.info(f"")

    #Show the GUI application
    main_view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
