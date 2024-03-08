"""
Main script for running web scraping tasks and scheduling their execution.

This script defines functions to run different web scraping tasks and schedule their execution if required.
It includes functions to run a job scraper using Scrapy, run the Europascraper module, and run a removal task
to delete old entries from the database. The main function initializes and starts multiple processes to run
these tasks concurrently. It also provides a signal handler to terminate processes gracefully upon receiving
a SIGINT signal (Ctrl+C).
"""

import argparse
import logging
import multiprocessing
import signal
import time

from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings
import schedule

from europascraper import europa
from db import db

from constants import CONSTANTS

# Prepare the logger
logging.basicConfig(level=logging.DEBUG)


def run_jobscraper():
    """
    Run the job scraper by initializing and starting the Scrapy process for each spider defined in the project settings.
    """
    try:
        settings = get_project_settings()
        spider_loader = SpiderLoader.from_settings(settings)
        process = CrawlerProcess(settings)
        for spider_name in spider_loader.list():
            process.crawl(spider_name)
        process.start()
    except Exception as e:
        logging.error(f"Error occurred in job scraper: {e}")
        exit(1)


def run_europascraper():
    """
    Run the Europascraper module.
    """
    try:
        europa.run()
    except Exception as e:
        logging.error(f"Error occurred in Europascraper: {e}")
        exit(1)


def _main():
    """
    Main function to initialize and start multiple processes for running different tasks.
    """
    db.init_database()

    # Start both scrapers and the removal module
    process_jobscraper = multiprocessing.Process(target=run_jobscraper)
    process_europascraper = multiprocessing.Process(target=run_europascraper)

    # Define a signal handler for SIGINT (Ctrl+C)
    def signal_handler(sig, frame):
        logging.info("Received Ctrl+C. Terminating processes...")
        process_jobscraper.terminate()
        process_europascraper.terminate()
        process_jobscraper.join()
        process_europascraper.join()
        logging.info("Processes terminated.")
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    process_jobscraper.start()
    process_europascraper.start()

    process_jobscraper.join(timeout=CONSTANTS["scrape_duration"])
    process_europascraper.join(timeout=CONSTANTS["scrape_duration"])

    # Check if any process is still alive and terminate if necessary
    if process_jobscraper.is_alive():
        process_jobscraper.terminate()
    if process_europascraper.is_alive():
        process_europascraper.terminate()

    # When the scraping is done, run the removal task once to remove entries
    # older than the interval specified in constants.py
    db.remove_old_entries()


def main():
    """
    Wrapper around main to prevent any crashes
    """
    try:
        _main()
    except Exception as e:
        logging.error(e)
        logging.debug("Will resume on the next scrape")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--schedule",
        action="store_true",
        help=f"Schedule the task to run daily at {CONSTANTS['scrape_time']} AM",
    )
    args = parser.parse_args()
    if args.schedule:
        schedule.every().day.at(CONSTANTS["scrape_time"]).do(main)
        logging.info(
            f"Task scheduled to run every day at {CONSTANTS['scrape_time']} AM."
        )
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        logging.info("Running task now.")
        main()
