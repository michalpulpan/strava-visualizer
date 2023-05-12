#!/usr/bin/env python3
"""
Python Strava visualizer using Strava API.
"""

__author__ = "Michal Pulpan"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
from logzero import logger
import json
import pandas as pd
from dotenv import load_dotenv

import scraper.scraper as scraper_module
import analyzer.cleaner as cleaner_module
import plotter.plotter as plotter_module
import analyzer.transformer as transformer_module

load_dotenv()


def main(args):
    """Main entry point of the app"""
    logger.info("App started")
    logger.info(args)

    if args.download:
        logger.info("Downloading data")
        scraper = scraper_module.Scraper()
        scraper()

    logger.info("Loading data")
    # load data from json
    with open("./data/activities.json", "r") as infile:
        data = json.load(infile)

    if not data:
        logger.error("No data loaded")
        return

    logger.info(f"Number of activities: {len(data)}")
    activities_raw = pd.json_normalize(data)
    print(
        activities_raw[["name", "distance", "average_speed", "moving_time"]].sample(5)
    )

    logger.info("Cleaning data")
    activities = cleaner_module.Cleaner(activities_raw)()
    # print(activities[["name", "distance", "average_speed", "moving_time"]].sample(5))

    logger.info("Data loaded")

    plotter = plotter_module.Plotter(activities)
    plotter.all_activities_plot()
    if args.heatmap:
        plotter.add_heatmap()

    if args.general_plot:
        plotter.general_plot()
        plotter.general_plot_weeks()

    if args.speed_elevation:
        plotter.speed_elevation_plot()

        # if args.elevation:
        #     logger.info("Getting elevation")
        #     scraper = scraper_module.Scraper()
        #     scraper.grab_elevation_data(activities)
        return
    if args.elevation:
        # plotter.plot_top_elevations()
        plotter.make_map_of_top_elevations()

    logger.info("App finished")


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

    parser.add_argument(
        "--heatmap",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--all_activities",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--general_plot",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--speed_elevation",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--elevation",
        action="store_true",
        default=False,
    )

    args = parser.parse_args()

    main(args)
