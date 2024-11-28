import argparse
import datetime
import logging
import os
import sys
import time
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from presenter.main_presenter import MainPresenter

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "critical": logging.CRITICAL,
}


def main():
    """Main function."""

    # add a command line argument to set the log level
    parser = argparse.ArgumentParser(description="Run the Sherds Match Assistance")
    parser.add_argument(
        "-l",
        "--log-level",
        choices=LOG_LEVELS.keys(),
        default="info",
        help="Set the logging level",
    )
    args = parser.parse_args()

    # Setting the logger and logging file, and make sure logging information goes to both the file and
    log_folder = Path(f"./logs/{os.getlogin()}")
    log_folder.mkdir(parents=True, exist_ok=True)
    log_filename = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_path = log_folder / log_filename

    logging.basicConfig(
        level=LOG_LEVELS[args.log_level],
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(str(log_path)), logging.StreamHandler()],
    )

    logger = logging.getLogger(__name__)
    logger.info("Log file: %s", log_path)

    # Setting the basic style
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Run the model, view and presenter one by one and count the time it takes to load each of them.
    logger.info("Starting up...")
    now = time.time()

    presenter = MainPresenter()
    logger.info("Started up in %s seconds", f"{time.time() - now:0.4f}")

    # Show the GUI application
    presenter.main_view.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
