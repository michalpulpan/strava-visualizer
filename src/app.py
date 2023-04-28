#!/usr/bin/env python3
"""
Python Strava visualizer using Strava API.
"""

__author__ = "Michal Pulpan"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
from logzero import logger
import os
from dotenv import load_dotenv

import scraper.scraper as scraper_module

load_dotenv()


def main(args):
    """Main entry point of the app"""
    logger.info("App started")
    logger.info(args)

    if args.download:
        logger.info("Downloading data")
        scraper = scraper_module.Scraper()
        scraper()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Optional argument flag which defaults to False
    parser.add_argument("-d", "--download", action="store_true", default=False)

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__),
    )

    args = parser.parse_args()

    main(args)
