import time
import nltk
import uvicorn
import schedule
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from dotenv import load_dotenv
from threading import Thread

from .utils.constants import RESULTS_PAGE_SIZE
from .config.pg_config import Database
from .utils.thesaurus import job_posting_thesaurus
from .utils.dateparser import parse_date
from .models.feedbackModel import FeedbackData
from .services.searchService import search
from .services.postgresService import get_database_constants
from .services.spellCheckerService import weighted_spell_check_query, suggest_query
from .services.feedbackService import save_feedback_to_database

load_dotenv()

nltk.download('stopwords')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('uvicorn')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


async def update_database_info(db: Database = None):
    try:
        if db is not None:
            app.state.N, app.state.DOC_IDS, app.state.ID2DATE = await get_database_constants(db, app.state.parsed_cache)
        else:
            app.state.N, app.state.DOC_IDS, app.state.ID2DATE = await get_database_constants(app.state.db,
                                                                                             app.state.parsed_cache)
        logger.info(f'Updated database info.')
    except Exception as e:
        logger.exception(e)


@app.on_event("startup")
async def startup_event():
    app.state.parsed_cache = {}
    app.state.parsed_cache = {"": parse_date("0001-01-01", datetime.now(), app.state.parsed_cache)}
    logger.info('Created app state parsed-dates cache.')

    database_instance = Database()
    await database_instance.connect()
    await update_database_info(database_instance)
    app.state.db = database_instance
    logger.info('Created database connection pool.')

    thread = Thread(target=run_periodically)
    thread.daemon = True
    thread.start()
    app.state.db_update_thread = thread
    schedule.every().day.at("06:00").do(update_database_info)

    logger.info("Server Startup")


@app.on_event("shutdown")
async def shutdown_event():
    if not app.state.db:
        await app.state.db.close()
    logger.info("Server Shutdown")


def expand_query(query):
    new_query = query
    for word in query.split():
        if word in job_posting_thesaurus:
            for synonym in job_posting_thesaurus[word]:
                new_query = new_query + " " + synonym
    return new_query


@app.get("/search/")
async def do_search(query: str, request: Request, page: int = 1):
    _start_time = time.time()
    if page < 1:
        raise HTTPException(status_code=400, detail='Page value must be equal or greater than 1.')
    response = None
    try:
        results, total_results = await search(query, request, page=page)
        response = {
            'data': {
                "query": query,
                "results": [{k: v for k, v in x.items()} for x in
                            results] if total_results > (page * RESULTS_PAGE_SIZE) - RESULTS_PAGE_SIZE else [],
                "total_results": total_results
            }
        }
    except Exception as e:  # General / Unknown error
        logger.exception(e)
        if response:
            raise HTTPException(status_code=500, detail=response)
        else:
            raise HTTPException(status_code=500, detail={
                'query': query,
                'message': f'Internal server error.'
            })

    if total_results > 0:
        return response
    else:
        raise HTTPException(status_code=404, detail={
            'query': query,
            'message': f'No results found for {query}.'
        })


@app.get("/suggest/")
async def route_query(query: str, request: Request):
    suggestions={weighted_spell_check_query(query)}
    suggestions.update(await suggest_query(query, request))
    return suggestions


@app.post("/submit_feedback/")
async def submit_feedback(feedback_data: FeedbackData, request: Request):
    try:
        # Save feedback data to the PostgreSQL database
        await save_feedback_to_database(feedback_data, request)

        return {"message": "Feedback submitted successfully."}
    except Exception as e:
        # Handle exceptions, log errors, and return appropriate response
        logging.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


def run_periodically():
    while True:
        schedule.run_pending()
        time.sleep(1)
        # Wait for 24 hours (86400 seconds)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006, log_level="info")
