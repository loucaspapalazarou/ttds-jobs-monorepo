import numpy as np

from itertools import product
from logging import getLogger

from ..utils.preprocessing import preprocess_query
from .redisService import get_index

logger = getLogger('uvicorn')

tokenization_regex_boolean = r'(\bAND\b|\bOR\b|\bNOT\b|\b\w+\b|[#"\(\)])'


def perform_phrase_search(query):
    postings = list(get_index(query).values())
    # Display Result
    common_doc_ids = set.intersection(
        *(set(posting.keys()) for posting in postings))  # perform intersection to get common docs
    final_doc_ids = set()
    if len(postings) > 1:
        for doc_id in common_doc_ids:
            positions = list(np.array([posting[doc_id].split(",") for posting in postings], dtype=int))
            combinations = list(
                product(*positions))  # calculate all combinations of positions of different tokens in a doc
            for combination in combinations:
                valid = all([combination[i] + 1 == combination[i + 1] for i in
                             range(len(combination) - 1)])  # checking if one token is followed by the other
                if valid:
                    final_doc_ids.add(int(doc_id))
                    break
        return final_doc_ids
    else:
        common_doc_ids = set(list(np.array(list(common_doc_ids), dtype=int)))
        return common_doc_ids


def perform_proximity_search(tokens, proximity_distance):
    postings = list(get_index(tokens).values())
    # Display Result
    common_doc_ids = set.intersection(
        *(list(posting.keys()) for posting in postings))  # perform intersection to get common docs
    final_doc_ids = set()
    if len(postings) > 1:
        for doc_id in common_doc_ids:
            positions = set(np.array([posting[doc_id].split(",") for posting in postings], dtype=int))
            combinations = list(
                product(*positions))  # calculate all combinations of positions of different tokens in a doc
            for combination in combinations:
                valid = all([abs(combination[i] - combination[i + 1]) <= proximity_distance for i in
                             range(len(combination) - 1)])  # checking if the distance is lower than the max distance
                if valid:
                    final_doc_ids.add(int(doc_id))
                    break
        return final_doc_ids
    else:
        common_doc_ids = set(list(np.array(list(common_doc_ids), dtype=int)))
        return common_doc_ids


def boolean_search(tokens, doc_ids) -> list:
    tokens = preprocess_query(tokens.split(' '))
    current_result = set(doc_ids)
    operators = []
    word_for_phrase = []
    phrase = False
    distance = 0
    proximity = False
    hashtag = False

    # boolean search
    # Difficulty while separating operators (boolean, proximity)
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
            word_for_phrase.append(token)  # if phrase or proximity search is being activated the words are added to
            # the list until the end is detected
        elif hashtag:
            distance = int(token)  # distance is set
            hashtag = False
        else:
            postings = get_index([token])[token]
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
                    term_postings = doc_ids - term_postings
    return list(current_result)
