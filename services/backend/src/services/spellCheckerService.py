from random import choices
from collections import Counter
from spellchecker import SpellChecker
from autocorrect import Speller
from textblob import TextBlob


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
        corrected_term = choices(corrections, weights=weights, k=1)[0]
    return corrected_term


def weighted_spell_check_query(query):
    corrected_query = []
    # Split the query into individual terms
    terms = query.split()
    for term in terms:
        corrected_term = weighted_spell_check_en(term)
        corrected_query.append(corrected_term)
    return " ".join(corrected_query)
