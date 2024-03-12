import re

from numpy import log10
from logging import getLogger
from fastapi import Request

from ..utils.preprocessing import preprocess_query, BOOL_OPERATORS
from ..utils.constants import RESULTS_PAGE_SIZE
from .redisService import get_index
from .booleanSearchService import boolean_search

logger = getLogger('uvicorn')


def ranked_search(tokens: list[str], n_docs, date_factors: dict) -> list[int]:
    scores = {}
    for term, document_entries in get_index(tokens).items():
        if not document_entries:
            continue
        idf = log10(n_docs / len(document_entries.keys()))
        for doc_id, idx_term in document_entries.items():
            date_factor = date_factors.get(doc_id, date_factors[''])
            doc_id = int(doc_id)
            tf = 1 + log10(len(idx_term.split(",")))
            scores[doc_id] = scores.get(doc_id, 0) + (tf * idf) * date_factor
    return sorted(scores, key=scores.get, reverse=True)


async def search(query, request: Request, page: int = 1, size: int = RESULTS_PAGE_SIZE):
    _query = preprocess_query(query.split(' '))
    _offset = (page * size) - size
    # BOOLEAN SEARCH
    if re.search('|'.join(BOOL_OPERATORS), ' '.join(_query)):
        doc_ids = boolean_search(query, request.app.state.DOC_IDS)
    # RANKED SEARCH
    else:
        # n_docs = await request.app.state.db.fetch_rows('SELECT count(*) as count FROM jobs')
        doc_ids = ranked_search(_query, request.app.state.N, request.app.state.ID2DATE)
    results = await request.app.state.db.fetch_rows(
        f'SELECT * FROM jobs WHERE id in ({",".join([str(d) for d in doc_ids[_offset:_offset + size]])})'
    )
    return results
