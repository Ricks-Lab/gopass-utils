"""
NAME
    SLOlogger.py - Centralized logging configuration.

DESCRIPTION
    This module defines overall project logging.

AVAILABILITY
    The SLOlogger.py module is part of the rickslab-sl-options package and is available
    from https://github.com/Ricks-Lab/SL-Options

LICENSE
    Copyright (C) 2025 Rick Langford, Natalya Langford - All Rights Reserved.
    Unauthorized copying of this file, via any medium, is strictly prohibited.
"""
__docformat__ = 'reStructuredText'

# pylint: disable=multiple-statements
# pylint: disable=line-too-long
# pylint: disable=logging-format-interpolation
# pylint: disable=consider-using-f-string
# pylint: disable=no-member

import logging
import sys
import os
from logging.handlers import RotatingFileHandler



def configure_logger(name: str = "",
                     log_level: int = logging.INFO,
                     log_dir: str = './',
                     log_file: str = __name__,
                     stream: bool = True) -> logging.Logger:
    """
    Configures and returns a logger with the specified name and log level.

    :param name: Name of the logger (usually __name__).
    :param log_level: Logging level (e.g., logging.DEBUG, logging.INFO).
    :param log_dir: Directory where log files are stored.
    :param log_file: Full pathname of log file (usually __name__).
    :param stream: Configure stream logger if True.
    :return: Configured logger instance.
    """
    # Ensure the log directory exists
    if log_dir != './':
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError:
            print("Configuration Error: Unable to create log directory at {}".format(log_dir))
            sys.exit(-1)

    # Create the logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid duplicate handlers if the logger is already configured
    if logger.hasHandlers():
        return logger

    # Define log format
    log_format_stream = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(module)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    log_format_file = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(module)s:%(lineno)d] %(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    if stream:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format_stream)
        logger.addHandler(console_handler)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=100 * 1024 * 1024,  # 100 MB
        backupCount=15  # Keep 15 backup files
    )
    file_handler.setFormatter(log_format_file)
    #logger.addHandler(file_handler)
    logger.info('Logger %s initialized.', name)

    logger.propagate = True

    return logger

