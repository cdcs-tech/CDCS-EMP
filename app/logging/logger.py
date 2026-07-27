"""
Logging Configuration
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(app):
    """
    Configure application logging.
    """

    log_directory = Path("logs")
    log_directory.mkdir(exist_ok=True)

    log_file = log_directory / "cdcs_emp.log"

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s "
        "[%(name)s] %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.info("CDCS-EMP application started.")
