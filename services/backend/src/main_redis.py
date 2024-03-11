from fastapi import APIRouter
import time
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import itertools
import numpy as np
import psycopg2
from tqdm import tqdm
from dateutil import parser
from datetime import datetime
import regex
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import re
import nltk
from langdetect import detect
from langcodes import Language
import redis
import uvicorn
import threading
from dotenv import load_dotenv
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import schedule
from spellchecker import SpellChecker
from autocorrect import Speller
from textblob import TextBlob
from collections import Counter
import random
import json
import logging
from http.client import HTTPException
from pydantic import BaseModel

current_script_dir = os.path.dirname(os.path.abspath(__file__))
grandparent_dir = os.path.dirname(os.path.dirname(current_script_dir))

# Add the grandparent directory to sys.path
if grandparent_dir not in sys.path:
    sys.path.append(grandparent_dir)

from utils.preprocessing import preprocess

load_dotenv()

nltk.download("stopwords")

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


r = redis.Redis(**REDIS_CONNECTION_CONFIG)

job_posting_thesaurus = {
    "developer": ["developer", "programmer", "coder", "software"],
    "data": ["data", "information", "intelligence"],
    "manager": ["manager", "supervisor", "team leader", "head", "director"],
    "remote": ["remote", "home", "virtual", "offsite", "telecommute", "distributed"],
    "full-time": ["full-time", "permanent"],
    "part-time": [
        "part-time",
        "temporary",
        "contract",
        "freelance",
        "hourly",
        "casual",
    ],
    "marketing": ["marketing", "SEO", "branding"],
    "writer": ["writer", "copywriter", "author", "editor"],
    "consultant": ["consultant", "advisor", "consulting", "strategy", "management"],
    "service": ["service", "support", "client service", "help"],
    "HR": ["HR", "human resources", "HR manager", "recruitment", "talent"],
    "finance": ["finance", "accountant", "auditor", "controller", "finance consultant"],
    "education": [
        "education",
        "teacher",
        "educator",
        "instructor",
        "professor",
        "tutor",
    ],
    "healthcare": ["healthcare", "nurse", "doctor", "medical", "pharmacist"],
    "intern": ["intern", "internship", "trainee", "apprentice"],
    "entry level": [
        "entry level",
        "junior",
        "associate",
        "beginner",
        "trainee",
        "starter",
    ],
    "senior": ["senior", "lead", "principal", "chief"],
    "executive": ["executive", "CEO", "CFO", "CTO"],
    "programmer": ["developer", "programmer", "coder", "software"],
    "coder": ["developer", "programmer", "coder", "software"],
    "software": ["developer", "programmer", "coder", "software"],
    "information": ["data", "information", "intelligence"],
    "intelligence": ["data", "information", "intelligence"],
    "supervisor": ["manager", "supervisor", "team leader", "head", "director"],
    "team leader": ["manager", "supervisor", "team leader", "head", "director"],
    "head": ["manager", "supervisor", "team leader", "head", "director"],
    "director": ["manager", "supervisor", "team leader", "head", "director"],
    "home": ["remote", "home", "virtual", "offsite", "telecommute", "distributed"],
    "virtual": ["remote", "home", "virtual", "offsite", "telecommute", "distributed"],
    "offsite": ["remote", "home", "virtual", "offsite", "telecommute", "distributed"],
    "telecommute": [
        "remote",
        "home",
        "virtual",
        "offsite",
        "telecommute",
        "distributed",
    ],
    "distributed": [
        "remote",
        "home",
        "virtual",
        "offsite",
        "telecommute",
        "distributed",
    ],
    "permanent": ["full-time", "permanent"],
    "temporary": [
        "part-time",
        "temporary",
        "contract",
        "freelance",
        "hourly",
        "casual",
    ],
    "contract": ["part-time", "temporary", "contract", "freelance", "hourly", "casual"],
    "freelance": [
        "part-time",
        "temporary",
        "contract",
        "freelance",
        "hourly",
        "casual",
    ],
    "hourly": ["part-time", "temporary", "contract", "freelance", "hourly", "casual"],
    "casual": ["part-time", "temporary", "contract", "freelance", "hourly", "casual"],
    "SEO": ["marketing", "SEO", "branding"],
    "branding": ["marketing", "SEO", "branding"],
    "copywriter": ["writer", "copywriter", "author", "editor"],
    "author": ["writer", "copywriter", "author", "editor"],
    "editor": ["writer", "copywriter", "author", "editor"],
    "advisor": ["consultant", "advisor", "consulting", "strategy", "management"],
    "consulting": ["consultant", "advisor", "consulting", "strategy", "management"],
    "strategy": ["consultant", "advisor", "consulting", "strategy", "management"],
    "management": ["consultant", "advisor", "consulting", "strategy", "management"],
    "support": ["service", "support", "client service", "help"],
    "client service": ["service", "support", "client service", "help"],
    "help": ["service", "support", "client service", "help"],
    "human resources": ["HR", "human resources", "HR manager", "recruitment", "talent"],
    "HR manager": ["HR", "human resources", "HR manager", "recruitment", "talent"],
    "recruitment": ["HR", "human resources", "HR manager", "recruitment", "talent"],
    "talent": ["HR", "human resources", "HR manager", "recruitment", "talent"],
    "accountant": [
        "finance",
        "accountant",
        "auditor",
        "controller",
        "finance consultant",
    ],
    "auditor": ["finance", "accountant", "auditor", "controller", "finance consultant"],
    "controller": [
        "finance",
        "accountant",
        "auditor",
        "controller",
        "finance consultant",
    ],
    "finance consultant": [
        "finance",
        "accountant",
        "auditor",
        "controller",
        "finance consultant",
    ],
    "teacher": ["education", "teacher", "educator", "instructor", "professor", "tutor"],
    "educator": [
        "education",
        "teacher",
        "educator",
        "instructor",
        "professor",
        "tutor",
    ],
    "instructor": [
        "education",
        "teacher",
        "educator",
        "instructor",
        "professor",
        "tutor",
    ],
    "professor": [
        "education",
        "teacher",
        "educator",
        "instructor",
        "professor",
        "tutor",
    ],
    "tutor": ["education", "teacher", "educator", "instructor", "professor", "tutor"],
    "nurse": ["healthcare", "nurse", "doctor", "medical", "pharmacist"],
    "doctor": ["healthcare", "nurse", "doctor", "medical", "pharmacist"],
    "medical": ["healthcare", "nurse", "doctor", "medical", "pharmacist"],
    "pharmacist": ["healthcare", "nurse", "doctor", "medical", "pharmacist"],
    "internship": ["intern", "internship", "trainee", "apprentice"],
    "trainee": ["entry level", "junior", "associate", "beginner", "trainee", "starter"],
    "apprentice": ["intern", "internship", "trainee", "apprentice"],
    "junior": ["entry level", "junior", "associate", "beginner", "trainee", "starter"],
    "associate": [
        "entry level",
        "junior",
        "associate",
        "beginner",
        "trainee",
        "starter",
    ],
    "beginner": [
        "entry level",
        "junior",
        "associate",
        "beginner",
        "trainee",
        "starter",
    ],
    "starter": ["entry level", "junior", "associate", "beginner", "trainee", "starter"],
    "lead": ["senior", "lead", "principal", "chief"],
    "principal": ["senior", "lead", "principal", "chief"],
    "chief": ["senior", "lead", "principal", "chief"],
    "CEO": ["executive", "CEO", "CFO", "CTO"],
    "CFO": ["executive", "CEO", "CFO", "CTO"],
    "CTO": ["executive", "CEO", "CFO", "CTO"],
}

connection = psycopg2.connect(**PG_CONNECTION_CONFIG)
DOC_IDS = []
N = 0
ID2DATE = {}

parsed_cache = {}


def parse_date(date_str, current_time, dayfirst=True):
    if date_str in parsed_cache:  # Return cached result if available
        return parsed_cache[date_str]
    try:
        # Parse the date with dayfirst option
        parsed_date = parser.parse(date_str, dayfirst=dayfirst)
        date_factor = current_time - parsed_date
        days_diff = abs(date_factor.days)
        date_factor = 1 / (
            1 + days_diff / 30
        )  # Adding 1 to avoid division by zero and ensure recent docs have higher factor
        parsed_cache[date_str] = date_factor  # Cache the result
        return date_factor
    except ValueError:
        print(f"Could not parse date: {date_str}")
        return None


min_date_value = parse_date("0001-01-01", datetime.now())
parsed_cache = {"": min_date_value}


def fetch_token(token):
    return r.hgetall(token)


def fetch_postings(query):
    with ThreadPoolExecutor(max_workers=10) as executor:
        postings_list = list(executor.map(fetch_token, query))
    return postings_list


def update_database_info():
    global DOC_IDS, N, ID2DATE
    query = f"""
        SELECT Count(*) FROM jobs;

        """

    cursor = connection.cursor()
    cursor.execute(query)
    N = cursor.fetchone()[0]  # Fetch the JSON result

    query = f"""
        SELECT json_agg(ID::INTEGER) FROM jobs;

        """

    cursor.execute(query)
    DOC_IDS = cursor.fetchone()[
        0
    ]  # DOC_IDS could be replace to ID2DATE.keys() if memory ussage is bad

    query = """
    SELECT json_object_agg(ID, date_posted) FROM jobs;
    """
    cursor = connection.cursor()
    cursor.execute(query)
    current_time = datetime.now()
    ID2DATE = cursor.fetchone()[
        0
    ]  # store the ID to Date to consider dates in the retrieval
    for key, value in tqdm(ID2DATE.items(), desc="Parsing dates"):
        ID2DATE[key] = parse_date(value, current_time)
    cursor.close()
    ID2DATE[""] = parse_date("", current_time)


app = FastAPI(title="Gateway", openapi_url="/openapi.json")

api_router = APIRouter()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def getAllDocs(positional_index):
    all_doc_ids = set()
    for term_data in positional_index.values():
        all_doc_ids.update(term_data["posting_list"].keys())
    return all_doc_ids


CURRENT_RESULT = []
compiled_patterns = {}
stemmers = {}
stemmed_languages = [
    "arabic",
    "danish",
    "dutch",
    "english",
    "finnish",
    "french",
    "german",
    "hungarian",
    "italian",
    "norwegian",
    "portuguese",
    "romanian",
    "russian",
    "spanish",
    "swedish",
]
non_alpha_pattern = regex.compile(r"\p{P}")


def desp_preprocessing(text):
    try:
        language_code = detect(text)
        language_full_form = Language.get(language_code).language_name().lower()
    except:
        language_full_form = "unknown"

    text = non_alpha_pattern.sub(" ", text)
    text = text.lower()
    if language_full_form in stemmed_languages:
        stopwords_by_language = set(stopwords.words(language_full_form))

        if language_full_form not in compiled_patterns:
            pattern = (
                r"\b(?:" + "|".join(map(re.escape, stopwords_by_language)) + r")\b"
            )
            compiled_patterns[language_full_form] = re.compile(pattern)

        text = compiled_patterns[language_full_form].sub(" ", text)

        if language_full_form not in stemmers:
            stemmers[language_full_form] = SnowballStemmer(language_full_form)
        stemmer = stemmers[language_full_form]

        words = [stemmer.stem(token) for token in text.split()]
    else:
        words = text.split()

    return words


def add_dates_to_score(Scores, connection):
    id_array = list(Scores.keys())
    query = """
    SELECT id, date_posted
    FROM jobs
    WHERE id = ANY(%s);
    """

    cursor = connection.cursor()
    cursor.execute(query, (id_array,))
    results = cursor.fetchall()


def optimized_tfidf(query, N_DOCS):
    tokens = preprocess(query)
    Scores = {}
    # Use pipeline to reduce the number of calls to Redis
    postings_list = fetch_postings(tokens)
    for postings in postings_list:
        if postings:
            df = len(postings)
            idf = np.log10(N_DOCS / df)
            for doc_id, idx_term in postings.items():
                idx_term_count = len(idx_term.split(","))
                date_factor = ID2DATE.get(doc_id, ID2DATE[""])
                tf = 1 + np.log10(idx_term_count)
                doc_id = int(doc_id)
                Scores[doc_id] = Scores.get(doc_id, 0) + tf * idf * date_factor
    sorted_docs = sorted(Scores, key=Scores.get, reverse=True)
    return sorted_docs

    # return [(doc_id, round(score, 4)) for doc_id, score in sorted_docs]


def perform_phrase_search(query):
    # tokens=pre_process(query)
    postings = fetch_postings(query)
    # Display Result
    common_doc_ids = set.intersection(
        *(set(posting.keys()) for posting in postings)
    )  # perform intersection to get common docs
    final_doc_ids = set()
    if len(postings) > 1:
        for doc_id in common_doc_ids:
            positions = [np.array(posting[doc_id].split(","), dtype=int) for posting in postings]
            combinations = list(
                itertools.product(*positions)
            )  # calculate all combinations of positions of different tokens in a doc
            for combination in combinations:
                valid = all(
                    [
                        combination[i] + 1 == combination[i + 1]
                        for i in range(len(combination) - 1)
                    ]
                )  # checking if one token is followed by the other
                if valid:
                    final_doc_ids.add(int(doc_id))
                    break
        return final_doc_ids
    else:
        common_doc_ids = set(list(np.array(list(common_doc_ids), dtype=int)))
        return common_doc_ids


def perform_proximity_search(tokens, PROX):
    # tokens=pre_process(tokens)
    postings = fetch_postings(tokens)
    # Display Result
    common_doc_ids = set.intersection(
        *(list(posting.keys()) for posting in postings)
    )  # perform intersection to get common docs
    final_doc_ids = set()
    if len(postings) > 1:
        for doc_id in common_doc_ids:
            positions = [np.array(posting[doc_id].split(","), dtype=int) for posting in postings]
            combinations = list(
                itertools.product(*positions)
            )  # calculate all combinations of positions of different tokens in a doc
            for combination in combinations:
                valid = all(
                    [
                        abs(combination[i] - combination[i + 1]) <= PROX
                        for i in range(len(combination) - 1)
                    ]
                )  # checking if the distance is lower than the max distance
                if valid:
                    final_doc_ids.add(int(doc_id))
                    break
        return final_doc_ids
    else:
        common_doc_ids = set(list(np.array(list(common_doc_ids), dtype=int)))
        return common_doc_ids


non_alpha_pattern_boolean = regex.compile(r'[^\w\s#"()]+')
logical_operators = {"AND", "OR", "NOT"}


def desp_preprocessing_boolean(text):
    try:
        language_code = detect(text)
        language_full_form = Language.get(language_code).language_name().lower()
    except:
        language_full_form = "unknown"

    # Removing punctuation except for '#'
    text = non_alpha_pattern_boolean.sub(" ", text)
    pattern = r"\b(?!AND\b|OR\b|NOT\b)\w+\b"
    # Use a lambda function to lower the matched words
    text = re.sub(pattern, lambda x: x.group().lower(), text)
    if language_full_form in stemmed_languages:
        stopwords_by_language = set(stopwords.words(language_full_form))
        # Preparing regex pattern without altering 'AND', 'NOT', 'OR'
        if language_full_form not in compiled_patterns:
            # Exclude 'AND', 'NOT', 'OR' from being treated as stopwords
            pattern_stopwords = stopwords_by_language - {"AND", "NOT", "OR"}
            pattern = r"\b(?:" + "|".join(map(re.escape, pattern_stopwords)) + r")\b"
            compiled_patterns[language_full_form] = re.compile(pattern)

        text = compiled_patterns[language_full_form].sub(" ", text)

        if language_full_form not in stemmers:
            stemmers[language_full_form] = SnowballStemmer(language_full_form)
        stemmer = stemmers[language_full_form]

        # Tokenizing while preserving 'AND', 'NOT', 'OR', and '#'
        tokens = re.findall(r'(\bAND\b|\bOR\b|\bNOT\b|\b\w+\b|[#"\(\)])', text)
        words = [
            token if token in logical_operators else stemmer.stem(token)
            for token in tokens
        ]
    else:
        # For languages not supported for stemming, tokenize while preserving specific tokens
        words = re.findall(r'(\bAND\b|\bOR\b|\bNOT\b|\b\w+\b|[#"\(\)])', text)
    return words


tokenization_regex_boolean = r'(\bAND\b|\bOR\b|\bNOT\b|\b\w+\b|[#"\(\)])'


# boolean search function
def boolean_search(tokens):
    ######## IMPORTANT#####
    # NOT REMOVING #,(,),""
    # CHECKING IF #WORK
    # COMPROBAR QUE EL TDIDF SE ORDENA DESCENDENTEMENTE Y ELIMINAR OR AND Y ETC DE LA REGEX

    tokens = preprocess(tokens, tokenization_regex=tokenization_regex_boolean)
    # doc_ids=set(getAllDocs(positional_index)) #if query is empty all docs are retrived
    current_result = set(DOC_IDS)
    operators = []
    word_for_phrase = []
    phrase = False
    distance = 0
    proximity = False
    hashtag = False
    # boolean search
    # Dificulty while separating operators (boolean, proximity)

    for token in tokens:
        if token in ["AND", "OR", "NOT"]:
            operators.append(token)  # appended to the stack of operators
        elif token == "#":  # next token should be maximum distance of proximity search
            hashtag = True
        elif token == "(":
            proximity = True  # next tokens should be added to a list and perform proximity search over that list
        elif token == ")":  # proximity search should be performed
            current_result &= perform_proximity_search(word_for_phrase, distance)
            word_for_phrase.clear()
            proximity = False
        elif token == '"':
            if not phrase:  # start of the phrase is detected
                phrase = True
            else:  # end of the phrase is detected search is performed
                current_result &= perform_phrase_search(word_for_phrase)
                word_for_phrase.clear()
                phrase = False
        elif phrase or proximity:
            word_for_phrase.append(
                token
            )  # if phrase or proximity search is being activated the words are added to the list until the end is detected
        elif hashtag:
            distance = int(token)  # distance is set
            hashtag = False
        else:
            postings = r.hgetall(token)
            # dict_word=positional_index.get(token)
            if postings is not None:  # word exist in the postings
                posting_numeric = np.array(list(postings.keys()), dtype=int)
                term_postings = set(list(posting_numeric))
            else:
                term_postings = set()
            if len(operators) == 0:
                current_result &= term_postings  # This is made for the first word
            while len(operators) > 0:
                operator = operators.pop()
                # perform operations in order of popping
                if operator == "AND":
                    current_result &= term_postings
                elif operator == "OR":
                    current_result |= term_postings
                elif operator == "NOT":
                    term_postings = DOC_IDS - term_postings
    return list(current_result)


def expand_query(query):
    new_query = query
    for word in query.split():
        if word in job_posting_thesaurus:
            for synonym in job_posting_thesaurus[word]:
                new_query = new_query + " " + synonym
    return new_query


def weighted_spell_check_en(term):
    # Weighted spell check using multiple libraries
    spellchecker = SpellChecker()
    autocorrect = Speller(lang="en")
    textblob = TextBlob(term)

    # Calculate weights for each library
    spellchecker_weight = 0.4
    autocorrect_weight = 0.3
    textblob_weight = 0.3

    # Spell check using each library
    spellchecker_correction = spellchecker.correction(term)
    autocorrect_correction = autocorrect(term)
    textblob_correction = str(textblob.correct())
    corrections = [spellchecker_correction, autocorrect_correction, textblob_correction]
    corrections_count = Counter(corrections)

    # Find the most common correction, if there's a tie, this returns one randomly
    most_common_correction, count = corrections_count.most_common(1)[0]

    if count > 1:  # If at least two libraries agree on the correction
        corrected_term = most_common_correction
    else:
        # No consensus; choose based on weights (simplified approach)
        weights = [spellchecker_weight, autocorrect_weight, textblob_weight]
        corrected_term = random.choices(corrections, weights=weights, k=1)[0]
    return corrected_term


def weighted_spell_check_query(query):
    corrected_query = []
    # Split the query into individual terms
    terms = query.split()
    for term in terms:
        corrected_term = weighted_spell_check_en(term)
        corrected_query.append(corrected_term)
    return " ".join(corrected_query)


@app.get("/suggest/")
async def route_query(query: str):
    return [weighted_spell_check_query(query)]
    # return suggestions


@app.get("/results/size")
async def get_results_size():
    return len(CURRENT_RESULT)


# CURRENT RESULT IS DESIGNED FOR PAGINATION, then establishing a page size is easey to keep track of the page and retrieve the actual docs
@app.get("/search/")
async def route_query(query: str, N_PAGE: int = Query(30, alias="page")):
    start = time.time()
    pattern = r'\b(AND|OR|NOT)\b|["#]'
    if re.search(pattern, query):
        global CURRENT_RESULT
        CURRENT_RESULT = boolean_search(query)
    else:
        query = expand_query(query)
        CURRENT_RESULT = optimized_tfidf(query, N)
    result = await retrieve_jobs(1, N_PAGE)
    print(time.time() - start)
    return result


def fetch_documents(indexes):
    indexes_str = ",".join([f"'{index}'" for index in indexes])
    query = f"""
        SELECT json_agg(j ORDER BY j.idx)
        FROM (
            SELECT j.*, x.idx
            FROM unnest(ARRAY[{indexes_str}]::int[]) WITH ORDINALITY AS x(id, idx)
            JOIN jobs j ON j.id = x.id
        ) AS j;

    """

    # Execute the query
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchone()[0]  # Fetch the JSON result

    cursor.close()
    return result


pagination_offset = 0

import json


@app.get("/jobs/")
async def retrieve_jobs(page: int = Query(1, alias="page"), number_per_page: int = Query(30, alias="page")):
    global pagination_offset
    start_index = (page - 1) * number_per_page
    end_index = start_index + number_per_page

    document_indexes_needed = CURRENT_RESULT[start_index:end_index]
    current_length = len(CURRENT_RESULT)
    documents_fetched = fetch_documents(document_indexes_needed)
    if documents_fetched:
        additional_docs_needed = number_per_page - len(documents_fetched)
    else:
        additional_docs_needed = number_per_page
    # If more documents are needed, fetch additional documents
    while additional_docs_needed > 0 and end_index < current_length:
        pagination_offset += additional_docs_needed
        # Adjust start and end indexes to fetch more documents
        new_start_index = end_index
        end_index = new_start_index + additional_docs_needed

        additional_indexes_needed = CURRENT_RESULT[new_start_index:end_index]

        additional_documents = fetch_documents(additional_indexes_needed)
        if additional_documents:
            documents_fetched.extend(additional_documents)
        additional_docs_needed = number_per_page - len(documents_fetched)

        # Update buffer size or break condition to avoid infinite loops if needed
    if not documents_fetched:
        documents_fetched = {}
    return documents_fetched


schedule.every().day.at("06:00").do(update_database_info)


def run_periodically():
    while True:
        schedule.run_pending()
        time.sleep(1)
        # Wait for 24 hours (86400 seconds)


update_database_info()
thread = threading.Thread(target=run_periodically)
# Daemon threads are killed when the main program exits
thread.daemon = True
thread.start()

app.include_router(api_router)


class FeedbackData(BaseModel):
    rating: int
    feedback: str
    email: str
    date: str


# Define the function to save feedback data to the PostgreSQL database
async def save_feedback_to_database(feedback_data: FeedbackData):
    insert_statement = """
    INSERT INTO feedback (rating, feedback, email, date)
    VALUES (%s, %s, %s, %s);
    """

    data_tuple = (
        feedback_data.rating,
        feedback_data.feedback,
        feedback_data.email,
        feedback_data.date,
    )

    try:
        cur = connection.cursor()
        cur.execute(insert_statement, data_tuple)
        connection.commit()
    except Exception as e:
        logging.error(f"Error: {e}")
        connection.rollback()
        return None
    finally:
        cur.close()


# Define the endpoint to submit feedback
@app.post("/submitfeedback/")
async def submit_feedback(feedback_data: FeedbackData):
    try:
        # Save feedback data to the PostgreSQL database
        await save_feedback_to_database(feedback_data)

        return {
            "message": f"Feedback submitted successfully. Rating: {feedback_data.rating}, Feedback: {feedback_data.feedback}, Email: {feedback_data.email}, Date: {feedback_data.date}"
        }
    except Exception as e:
        # Handle exceptions, log errors, and return appropriate response
        logging.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006, log_level="debug")
