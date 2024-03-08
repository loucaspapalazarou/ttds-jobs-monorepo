import os
import time
import psycopg2
import redis
import tqdm
import regex
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import re
import nltk
from langdetect import detect
from langcodes import Language
from dotenv import load_dotenv
from multiprocessing import Pool
import sys
from pathlib import Path
from constants import CONSTANTS
from indexer.preprocessing import preprocess

REDIS_CONNECTION_CONFIG = {
    'host': CONSTANTS['REDIS_HOST'],
    'port': CONSTANTS['REDIS_PORT'],
    'db':0,
    #'password': os.getenv('REDIS_PASSWORD'),
    'decode_responses': True,
}


JOBS_POOL_CURSOR_NAME = os.getenv('JOBS_POOL_CURSOR_NAME', default='JOBS_POOL_CURSOR')
JOBS_POOL_CURSOR_SIZE = int(os.getenv('JOBS_POOL_CURSOR_SIZE', default=2000))

JOB_INDEX_START_POSITION = int(os.getenv('JOBS_INDEX_START_POSITION', default=0))
JOBS_INDEX_END_POSITION = os.getenv('JOBS_INDEX_END_POSITION', default=10_000)


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
        doc_id=doc[len(doc)-1]
        txt= f"{doc[2]} {doc[3]} {doc[5]} {doc[6]}"
        for pos, term in enumerate(preprocess(txt)):
            if term not in index.keys():
                index[term] = {doc_id: str(pos)}
            elif doc[0] not in index[term].keys():
                index[term][doc_id] = str(pos)
            else:
                index[term][doc_id] += f',{pos}'
    del documents
    return index

def build_index_individual(doc:list[str], doc_id:int) -> dict:
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
    txt= f"{doc[2]} {doc[3]} {doc[5]} {doc[6]}"
    for pos, term in enumerate(preprocess(txt)):
        if term not in index.keys():
            index[term] = {doc_id: str(pos)}
        elif doc_id not in index[term].keys():
            index[term][doc_id] = str(pos)
        else:
            index[term][doc_id] += f',{pos}'
    del doc
    return index


def update_remote_index(index: dict) -> bool:
    with redis.Redis(**REDIS_CONNECTION_CONFIG) as rd_connection:
        pipe = rd_connection.pipeline()
        [pipe.hset(term, mapping=data) for term, data in index.items()]
        pipe.execute()
    del index
    return True

def update_remote_index_individual(documents: list[str], doc_id:int) -> bool:
    index=build_index_individual(documents, doc_id)
    with redis.Redis(**REDIS_CONNECTION_CONFIG) as rd_connection:
        pipe = rd_connection.pipeline()
        [pipe.hset(term, mapping=data) for term, data in index.items()]
        pipe.execute()
    del index
    return True

def remove_entries_from_docs(documents, doc_ids_to_remove):
    # Create a pipeline
    with redis.Redis(**REDIS_CONNECTION_CONFIG) as rd_connection:
        pipe = rd_connection.pipeline()
        
        # Iterate over each document in the list of documents
        for doc in documents:
            # Assuming each document is a list of tokens
            preprocessed_doc=preprocess(doc)
            for token in preprocessed_doc:
                # Stack the hdel operation for the preprocessed token and the doc_ids to remove
                # *doc_ids_to_remove unpacks the list of doc_ids into separate arguments for hdel
                pipe.hdel(token, *doc_ids_to_remove)
        
        # Execute all stacked operations in the pipeline at once
        results = pipe.execute()


def index_database_segment(data_chunk: list[list[str]]) -> float:
    t = time.perf_counter()
    
    update_remote_index(data_chunk)
    del data_chunk
            # print(f"Excecueted batch {offset}-{offset + JOBS_POOL_CURSOR_SIZE} "
            #       f"Batch execution time:{time.perf_counter() - t:.2f} seconds")
    return time.perf_counter() - t


def divide_chunks(data, n):
    # Looping till length data
    for i in range(0, len(data), n):
        yield data[i:i + n]

# if __name__ == '__main__':
#     start_time = time.perf_counter()
#     r = redis.Redis(host='localhost', port=6379, db=0,decode_responses= True)
#     r.flushdb()
#     N = int(JOBS_INDEX_END_POSITION) if JOBS_INDEX_END_POSITION else None
#     with psycopg2.connect(**PG_CONNECTION_CONFIG) as conn:
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT Count(id) FROM jobs;")
#             N = int(cursor.fetchone()[0])
#             print(N)
        
#         with conn.cursor() as cursor:
#             cursor.execute(f"""
#             SELECT * FROM JOBS
#             WHERE id <= {JOBS_INDEX_END_POSITION}  
#             ORDER BY id;
#             """)
#             results=cursor.fetchall()
#         print("RESULTS FETCHED")
#         chunks = list(divide_chunks(results, JOBS_POOL_CURSOR_SIZE))
#         with Pool() as pool:
#             inputs = range(0, N + JOBS_POOL_CURSOR_SIZE, JOBS_POOL_CURSOR_SIZE)
#             execution_times = [x for x in tqdm.tqdm(pool.imap_unordered(index_database_segment, chunks), total=len(chunks))]
#     print("--- %s seconds ---" % (time.perf_counter() - start_time))
#     r = redis.Redis(host='localhost', port=6379, db=0)
#     random_key = r.randomkey().decode('utf-8')
#     print(random_key)
#     # Fetch the value of the random key
#     value = r.hgetall(random_key)
#     print(f"Random key: {random_key} has value: {value}")
        
if __name__ == "__main__":
    job_data_tuple = (
        'job-1',
    'https://example.com/job1',  # link
    'Software Developer',        # title
    'Example Company',           # company
    '2023-03-01',                # date_posted
    'New York, NY',              # location
    'This is a description  description of the job.'  # description
    )
    update_remote_index_individual(job_data_tuple,1)