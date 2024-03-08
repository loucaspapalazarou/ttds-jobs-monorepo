"""
Define item pipelines for processing scraped items.

This module contains two pipelines: `JobscraperMongoPipeline` and `JobscraperPostgresPipeline`.
`JobscraperMongoPipeline` is used for storing scraped items in a MongoDB database,
while `JobscraperPostgresPipeline` is used for storing items in a PostgreSQL database.

Note: The `JobscraperMongoPipeline` is not used but is kept as an archival example.

"""

import os
import psycopg2
import pymongo
from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
from pymongo.server_api import ServerApi
from constants import CONSTANTS
from db import db
from indexer.indexer import update_remote_index_individual


class JobscraperMongoPipeline:
    """
    Pipeline for storing scraped items in MongoDB.

    This pipeline stores scraped items in a MongoDB database.

    Attributes:
        connection: A pymongo.MongoClient instance for connecting to MongoDB.
        collection: A pymongo.collection.Collection instance representing the MongoDB collection.
    """

    def __init__(self) -> None:
        settings = get_project_settings()
        self.connection = pymongo.MongoClient(
            host=os.getenv("MONGODB_HOSTNAME"),
            port=os.getenv("MONGODB_PORT"),
            server_api=ServerApi("1"),
        )
        db = self.connection[os.getenv("MONGODB_DBATABASE")]
        self.collection = db[os.getenv("MONGODB_COLLECTION")]

    def process_item(self, item, spider):
        """
        Process and store the scraped item in MongoDB.

        Args:
            item: The scraped item to be processed.
            spider: The Spider instance that scraped the item.

        Returns:
            The processed item.
        """
        # Prepare the filter and update document
        filter_doc = {"id": item["id"]}  # Assuming 'id' is the field in item
        update_doc = {"$setOnInsert": dict(item)}  # Fields to set on insert

        # Update the collection, insert if the id does not exist
        self.collection.update_one(
            filter_doc, update_doc, upsert=True  # Ensures insert if not exists
        )
        return item


class JobscraperPostgresPipeline:
    """
    Pipeline for storing scraped items in PostgreSQL.

    This pipeline stores scraped items in a PostgreSQL database.

    Attributes:
        None
    """

    def __init__(self) -> None:
        db.init_database()

    def process_item(self, item, spider):
        """
        Process and store the scraped item in PostgreSQL.

        Args:
            item: The scraped item to be processed.
            spider: The Spider instance that scraped the item.

        Returns:
            The processed item.
        """
        data_tuple = (
            item.get("job_id", ""),
            item.get("link", ""),
            item.get("title", ""),
            item.get("company", ""),
            item.get("date_posted", ""),
            item.get("location", ""),
            item.get("description", ""),
        )
        
        doc_id=db.insert(data_tuple)
        if doc_id:
            update_remote_index_individual(data_tuple, doc_id)
        return item
