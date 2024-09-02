import sys
import logging
import time
from pathlib import Path
import getpass
from time import ctime

from PyQt5.QtWidgets import QApplication
from model.main_model import MainModel
from view.main_view import MainView
from presenter.main_presenter import MainPresenter


def main():
    """Main function."""

    # Setting the logger and logging file, and make sure logging information goes to both the file and
    log_folder = f"./logs/{getpass.getuser()}"
    log_path = f"{log_folder}/{ctime().replace(':','')}.txt"
    Path(log_folder).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_path), logging.StreamHandler()],
    )

    # Setting the basic style
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Run the model, view and presenter one by one and count the time it takes to load each of them.
    now = time.time()
    main_model = MainModel()
    logging.info("main_model %s seconds have passed", (time.time() - now))
    now = time.time()
    main_view = MainView()
    logging.info("main_view %s seconds have passed", (time.time() - now))
    now = time.time()
    main_presenter = MainPresenter(main_model, main_view)
    logging.info("main_presenter %s seconds have passed", (time.time() - now))
    logging.info("")

    # Show the GUI application
    main_view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
