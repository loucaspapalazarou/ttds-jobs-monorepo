import psycopg2
from constants import CONSTANTS


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
        ON CONFLICT (job_id) DO NOTHING;
        """

    try:
        cur.execute(insert_statement, data_tuple)
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        cur.close()
        connection.close()


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
        DELETE FROM jobs WHERE timestamp < NOW() - INTERVAL '{CONSTANTS["deletion_interval"]}';    
        """
    )
    connection.commit()
    cur.close()
    connection.close()
