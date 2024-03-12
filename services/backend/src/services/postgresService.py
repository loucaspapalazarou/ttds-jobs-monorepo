import json

from logging import getLogger
from datetime import datetime

from ..config.pg_config import Database
from ..utils.dateparser import parse_date

logger = getLogger('uvicorn')


async def get_database_constants(db: Database, dates_cache: dict) -> (int, list, dict):
    logger.info('Getting database constants...')
    n_docs = await db.fetch_rows('SELECT count(ID) as count FROM jobs')
    docs_and_dates = await db.fetch_rows('SELECT json_object_agg(ID, date_posted) as data FROM jobs;')

    id2date = json.loads(docs_and_dates[0].get('data'))
    doc_ids = list(id2date.keys())

    current_time = datetime.now()
    for key, value in id2date.items():
        id2date[key] = parse_date(value, current_time, dates_cache)
    id2date[""] = parse_date("", current_time, dates_cache)

    return n_docs[0].get('count'), doc_ids, id2date
