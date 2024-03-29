import re
import nltk
import os
import dotenv

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from langdetect import detect, LangDetectException
from langcodes import Language

dotenv.load_dotenv()

nltk.download('stopwords')
nltk.download('wordnet')

# (&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;|&cent;|&pound;|&yen;|&euro;|&copy;|&reg;|&#768;|&#769;|&#770;|&#771;|&#768;|&#769;|&#770;|&#771;|&#160;|&#60;|&#62;|&#38;|&#34;|&#39;|&#162;|&#163;|&#165;|&#8364;|&#169;|&#174;|\W|\d)+
TOKENIZATION_REGEX = os.getenv('TOKENIZATION_REGEX')

stemmed_languages = ["arabic", "danish", "dutch", "english", "finnish", "french", "german",
                     "hungarian", "italian", "norwegian", "portuguese", "romanian", "russian",
                     "spanish", "swedish"]

NOT = 'NOT'
AND = 'AND'
OR = 'OR'
BOOL_OPERATORS = NOT, AND, OR

SEPARATOR = ' % '


def detect_language(text: str) -> str:
    try:
        language_code = detect(text)
        language_full_form = Language.get(language_code).language_name().lower()
    except LangDetectException:
        language_full_form = 'unknown'
    return language_full_form


def preprocess(
        text: str,
        stop: bool = True,
        stem: bool = True,
        tokenization_regex: str = TOKENIZATION_REGEX,
        boolean: bool = False
) -> list[str]:
    """
    Preprocesses text applying tokenization, case folding, stoping and stemming.

    Parameters
    ----------
    text : list[str]
        list of strings to preprocess
    stop : bool, optional
        triggers stopping (defaults to `True`)
    stem : bool, optional
        triggers stemming (defaults to `True`)
    tokenization_regex : str, optional
        regular expression used for tokenization.
    boolean : bool, optional
        triggers boolean search behaviour (defaults to `False`)

    Returns
    -------
    preprocessed_strings : list[str]
        list of preprocessed strings.
    """

    def tokenize(string_to_split: str, regex: str = TOKENIZATION_REGEX) -> list[str]:
        """Apply tokenization to string"""
        if not boolean:
            split_string = re.split(regex, string_to_split)
            return [x for x in split_string if x and x != ' ']
        regex = r"(&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;|&cent;|&pound;|&yen;|&euro;|&copy;|&reg;|&#768;|&#769;|&#770;|&#771;|&#160;|&#60;|&#62;|&#38;|&#162;|&#163;|&#165;|&#8364;|&#169;|&#174;|[^\w\d\"()#])+"
        split_string = re.split(regex, string_to_split)
        special_char_pattern = r'(["#()])'
        tokens = []
        for x in split_string:
            if x and x != ' ':
                spaced_token = re.sub(special_char_pattern, r' \1 ', x)
                split_tokens = spaced_token.split()
                tokens.extend(split_tokens)
        return tokens

    def case_fold(strings_to_fold: list[str], bool_operators: list[str] = BOOL_OPERATORS) -> list[str]:
        """Apply case folding to list of strings"""
        if not boolean:
            return [x.lower() for x in strings_to_fold]
        return [x.lower()  if x not in bool_operators else x for x in strings_to_fold]

    def filter_stop_words(term_list: list[str], language: str, bool_operators: list[str] = BOOL_OPERATORS) -> list[str]:
        """Filter stop words in list of strings"""
        if not boolean:
            return [t for t in term_list if t not in stopwords.words(language)]
        return [t for t in term_list if t not in stopwords.words(language) or t in bool_operators]

    def stem_words(term_list: list[str], language: str, bool_operators: list[str] = BOOL_OPERATORS) -> list[str]:
        """Apply stemming to list of strings"""
        stemmer = SnowballStemmer(language)
        if not boolean:
            return [stemmer.stem(t) for t in term_list]
        return [token if token in bool_operators else stemmer.stem(token) for token in term_list]

    lang = detect_language(text)
    terms = case_fold(tokenize(text, tokenization_regex))
    if stop and lang in stemmed_languages:
        terms = filter_stop_words(terms, lang)
    if stem and lang in stemmed_languages:
        terms = stem_words(terms, lang)
    return terms


def preprocess_query(query: list[str]) -> list[str]:
    """
    Apply preprocessing to query.

    Parameters
    ----------
    query : list[str]
        query to be preprocessed (split by spaces).

    Returns
    -------
    preprocessed_query : list[str]
        query after preprocessing is applied.
    """
    _query_str = ' ' + ' '.join(query) + ' '

    # Do query preprocessing
    _terms = ((' ' + _query_str + ' ').replace(' ' + AND + ' ', SEPARATOR).replace(' ' + OR + ' ', SEPARATOR)
              .replace(' ' + NOT + ' ', SEPARATOR).split(SEPARATOR))  # Remove boolean Keywords
    _bool_operators = list(filter(lambda x: x in BOOL_OPERATORS, query))  # Get list of bool operators
    _preprocessed_terms = [' '.join(y) for y in [preprocess(x) for x in _terms]]  # apply preprocessing to query terms

    #   Reintroduce boolean operators into query list
    _preprocessed_query = []
    for i, term in enumerate(_preprocessed_terms):
        _preprocessed_query.append(term)
        if i < len(_preprocessed_terms) - 1:
            _preprocessed_query.append(_bool_operators[i])

    return ' '.join(_preprocessed_query).split(' ')  # Return preprocessed query as list of strings
