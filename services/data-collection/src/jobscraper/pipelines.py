"""
Define item pipelines for processing scraped items.

This module contains two pipelines: `JobscraperMongoPipeline` and `JobscraperPostgresPipeline`.
`JobscraperMongoPipeline` is used for storing scraped items in a MongoDB database,
while `JobscraperPostgresPipeline` is used for storing items in a PostgreSQL database.

Note: The `JobscraperMongoPipeline` is not used but is kept as an archival example.

"""

from db import db
from indexer.indexer import update_remote_index_individual


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

        doc_id = db.insert(data_tuple)
        if doc_id:
            update_remote_index_individual(data_tuple, doc_id)
        return item
