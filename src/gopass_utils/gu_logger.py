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

def configure_logger(name: str = "", log_level: int = logging.INFO, stream: bool = True) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if logger.hasHandlers():
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(module)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    if stream:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

    logger.propagate = False
    logger.info("Logger %s initialized", name)
    return logger
