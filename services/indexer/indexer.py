import os
import time

import psycopg2
import redis
import tqdm

from services.utils.preprocessing import preprocess
from dotenv import load_dotenv
from multiprocessing import Pool

load_dotenv()

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


def build_index(documents: list[list[str]]) -> dict:
    """
    Builds the index for the given document

    Parameters
    ----------
    documents : list[str]
        contains the content of the documents.

    Returns
    -------
    index : dict
        dictionary containing the built index.
    """
    index = {}
    for doc in documents:
        for pos, term in enumerate(preprocess((doc[1]))):
            if term not in index.keys():
                index[term] = {doc[0]: str(pos)}
            elif doc[0] not in index[term].keys():
                index[term][doc[0]] = str(pos)
            else:
                index[term][doc[0]] += f",{pos}"
    del documents
    return index


def update_remote_index(index: dict) -> bool:
    with redis.Redis(**REDIS_CONNECTION_CONFIG) as rd_connection:
        pipe = rd_connection.pipeline()
        [pipe.hset(term, mapping=data) for term, data in index.items()]
        pipe.execute()
    del index
    return True


def index_database_segment(offset: int = 0) -> tuple[int, float]:
    t = time.perf_counter()
    while True:
        try:
            with psycopg2.connect(**PG_CONNECTION_CONFIG) as pg_connection:
                with pg_connection.cursor() as cursor:
                    cursor.execute(
                        f"""
                    SELECT * FROM {FETCH_ALL_JOBS_VIEW} 
                    WHERE id > {offset} AND id <= {offset + JOBS_POOL_CURSOR_SIZE}  
                    ORDER BY id;
                    """
                    )
                    data = cursor.fetchall()
            update_remote_index(build_index(data))
            del data
            return offset, time.perf_counter() - t
        except Exception as e:
            print(e)
            print("PG DB Connection lost, reconnecting ...")


if __name__ == "__main__":
    start_time = time.perf_counter()

    N = int(JOBS_INDEX_END_POSITION) if JOBS_INDEX_END_POSITION else None
    if not N:
        with psycopg2.connect(**PG_CONNECTION_CONFIG) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT Count(id) FROM jobs;")
                N = int(cursor.fetchone()[0])
                print(N)

    with Pool(processes=NUMBER_OF_THREADS) as pool:
        inputs = range(0, N + JOBS_POOL_CURSOR_SIZE, JOBS_POOL_CURSOR_SIZE)
        execution_times = [
            x
            for x in tqdm.tqdm(
                pool.imap_unordered(index_database_segment, inputs), total=len(inputs)
            )
        ]

    [print(f"{x[0]:9} | {x[1]}") for x in execution_times]
    print("--- %s seconds ---" % (time.perf_counter() - start_time))
