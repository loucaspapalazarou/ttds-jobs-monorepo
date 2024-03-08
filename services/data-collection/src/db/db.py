import psycopg2
from constants import CONSTANTS
import redis
from indexer.preprocessing import preprocess

REDIS_CONNECTION_CONFIG = {
    'host': CONSTANTS['REDIS_HOST'],
    'port': CONSTANTS['REDIS_PORT'],
    'db':0,
    #'password': os.getenv('REDIS_PASSWORD'),
    'decode_responses': True,
}

def _create_db_connection():
    """
    Create a db connection

    returns: A db connection object
    """
    return psycopg2.connect(
        host=CONSTANTS["postgres_host"],
        user=CONSTANTS["postgres_user"],
        password=CONSTANTS["postgres_password"],
        dbname=CONSTANTS["postgres_db"],
    )
   
 


def init_database():
    """
    Initialize the database.

    This function connects to the PostgreSQL database specified in the constants module
    and creates a 'jobs' table if it doesn't exist already.

    """
    connection = _create_db_connection()
    cursor = connection.cursor()

    # Create table if it doesn't exist
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs(
            id SERIAL PRIMARY KEY,
            job_id VARCHAR(255) UNIQUE,
            link VARCHAR(255),
            title VARCHAR(255),
            company VARCHAR(255),
            date_posted VARCHAR(255),
            location VARCHAR(255),
            description text,
            timestamp timestamp DEFAULT current_timestamp
        );
        """
    )

    connection.commit()
    cursor.close()
    connection.close()


def insert(data_tuple):
    """
    Insert data into the 'jobs' table.

    Args:
        data_tuple (tuple): A tuple containing data to be inserted into the 'jobs' table.

    """
    connection = _create_db_connection()
    cur = connection.cursor()

    insert_statement = """
        INSERT INTO jobs (job_id, link, title, company, date_posted, location, description)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (job_id) DO NOTHING
        RETURNING id;
        """
    try:
        cur.execute(insert_statement, data_tuple)
        connection.commit()
        job_id = cur.fetchone()[0]
        print(job_id)
        return job_id
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        cur.close()
        connection.close()

def remove_entries_from_docs(documents, doc_ids_to_remove):
    # Create a pipeline
    with redis.Redis(**REDIS_CONNECTION_CONFIG) as rd_connection:
        pipe = rd_connection.pipeline()
        
        # Iterate over each document in the list of documents
        for doc in documents:
            preprocessed_doc=preprocess(doc[0])
            for token in preprocessed_doc:                # Stack the hdel operation for the preprocessed token and the doc_ids to remove
                # *doc_ids_to_remove unpacks the list of doc_ids into separate arguments for hdel
                pipe.hdel(token, *doc_ids_to_remove)
        
        # Execute all stacked operations in the pipeline at once
        results = pipe.execute()
        return True


def remove_old_entries():
    """
    Remove old entries from the 'jobs' table.

    This function deletes rows from the 'jobs' table where the timestamp is older than the deletion interval
    specified in the constants module.

    """
    connection = _create_db_connection()
    cur = connection.cursor()
    cur.execute(
        f"""
        SELECT json_agg(ID::text) FROM jobs WHERE timestamp < NOW() - INTERVAL '{CONSTANTS["deletion_interval"]}';    
        """
    )
    ids_to_remove=cur.fetchone()[0]
    cur.execute(
        f"""
    SELECT CONCAT_WS(' ', title, company, location, description) AS concatenated_string
    FROM jobs
    WHERE id::text = ANY(%s);
    """
    , (ids_to_remove,))
    documents_to_remove=cur.fetchall()
    remove_entries_from_docs(documents_to_remove, ids_to_remove)

    cur.execute(
        f"""
        DELETE FROM jobs WHERE WHERE id::text = ANY(%s)';    
        """
    , (ids_to_remove,))
    connection.commit()
    cur.close()
    connection.close()

if __name__ == "__main__":
    init_database()
    job_data_tuple = (
        'job-1',
    'https://example.com/job1',  # link
    'Software Developer',        # title
    'Example Company',           # company
    '2023-03-01',                # date_posted
    'New York, NY',              # location
    'This is a description  description of the job.'  # description
)
    insert(job_data_tuple)
