import re

from numpy import log10
from fastapi import Request

from ..utils.preprocessing import preprocess
from ..utils.constants import RESULTS_PAGE_SIZE
from .redisService import get_index
from .booleanSearchService import boolean_search


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
    _offset = (page * size) - size
    pattern = r'\b(AND|OR|NOT)\b|["#]'

    if re.search(pattern, query):   # BOOLEAN SEARCH
        doc_ids = boolean_search(query, request.app.state.DOC_IDS)
    else:   # RANKED SEARCH
        doc_ids = ranked_search(preprocess(query), request.app.state.N, request.app.state.ID2DATE)

    results = await request.app.state.db.fetch_rows(
        f"""
        SELECT json_agg(js ORDER BY js.idx) FROM (
            SELECT 
               j.id,
               j.job_id,
               j.link,
               j.title,
               j.company,
               j.date_posted,
               j.location,
               substr(j.description, 1, 500) || '...' as description,
               j.timestamp,
             x.idx
            FROM unnest(ARRAY[{",".join([str(d) for d in doc_ids[_offset:_offset + size]])}]::int[]) 
                WITH ORDINALITY AS x(id, idx)
            JOIN jobs j ON j.id = x.id
        ) AS js;
        """
    )

    return results, len(doc_ids)
