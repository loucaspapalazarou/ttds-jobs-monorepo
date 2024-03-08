from dotenv import load_dotenv
import os

load_dotenv()

CONSTANTS = {
    "postgres_host": os.getenv("PG_HOSTNAME"),
    "postgres_user": os.getenv("PG_USERNAME"),
    "postgres_password": os.getenv("POSTGRES_PASSWORD"),
    "postgres_db": os.getenv("PG_DB_NAME"),
    "scrape_duration": 14_400,  # 14,400 seconds = 4 hours
    "scrape_time": "00:00",
    "deletion_interval": "20 days",
}
