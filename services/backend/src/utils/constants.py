import os

PG_CONNECTION_CONFIG = {
    "host": os.getenv("PG_HOSTNAME"),
    "dbname": os.getenv("PG_DB_NAME"),
    "user": os.getenv("PG_USERNAME"),
    "port": os.getenv("PG_PORT"),
    "password": os.getenv("PG_PASSWORD"),
}

REDIS_CONNECTION_CONFIG = {
    "host": os.getenv("REDIS_HOST"),
    "port": os.getenv("REDIS_PORT"),
    "password": os.getenv("REDIS_PASSWORD"),
    "decode_responses": True,
}

FETCH_ALL_JOBS_VIEW = os.getenv("FETCH_ALL_JOBS_VIEW")

JOBS_POOL_CURSOR_NAME = os.getenv("JOBS_POOL_CURSOR_NAME", default="JOBS_POOL_CURSOR")
JOBS_POOL_CURSOR_SIZE = int(os.getenv("JOBS_POOL_CURSOR_SIZE", default=2000))

JOB_INDEX_START_POSITION = int(os.getenv("JOBS_INDEX_START_POSITION", default=0))
JOBS_INDEX_END_POSITION = os.getenv("JOBS_INDEX_END_POSITION", default=None)

NUMBER_OF_THREADS = int(os.getenv("NUMBER_OF_THREADS", default=5))

RESULTS_PAGE_SIZE = int(os.getenv("RESULTS_PAGE_SIZE", default=10))

PROX_REGEX = os.getenv("PROX_REGEX")
PHRASE_REGEX = os.getenv("PHRASE_REGEX")
PROXIMITY_MAX_DISTANCE = os.getenv("PROXIMITY_MAX_DISTANCE")
