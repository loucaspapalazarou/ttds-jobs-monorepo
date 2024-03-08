import psycopg2
from urllib.parse import quote_plus
from pymongo import MongoClient
from tqdm import tqdm
import time
import regex
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import re
import nltk
from langdetect import detect
from langcodes import Language

nltk.download('stopwords')
nltk.download('wordnet')

hostname = 'ms0806.utah.cloudlab.us'
database = 'jobs_db'
username = 'root'
port = 5432
password = 'root'  #

positional_index={}

non_alpha_pattern = regex.compile(r'\p{P}') #regex for splitting on non letter


def desp_preprocessing(text):
    if text !='':
        try:
            # Detect the language
            language_code = detect(text)

            if language_code !='No features in text.':
                # Get the full form of the detected language
                language_full_form = Language.get(language_code).language_name()
            else:
                language_full_form='unknown'
                
        except :
            language_full_form='unknown'
            print("Error:")
    else:
        return ['description empty']
    
    text=non_alpha_pattern.sub(" ", text)
    
    
    # Split tokens containing hyphens into separate tokens
    

    
    # Remove stopwords

    # List of languages for stopwords removal
    stemmed_languages = ["arabic","danish","dutch","english","finnish","french","german","hungarian","italian","norwegian","portuguese","romanian","russian","spanish","swedish"]

    # Remove stopwords for that language
    if language_full_form.lower() in stemmed_languages:
        # Get stopwords for the current language
        stopwords_by_language = set(stopwords.words(language_full_form.lower()))
        pattern = r'\b(?:' + '|'.join(stopwords_by_language) + r')\b' #regex for matching stopwords
        # Remove stopwords
        text = re.sub(pattern, ' ', text)
        stemmer = SnowballStemmer(language_full_form.lower())
        words = [stemmer.stem(token) for token in text.split()]  # Stem each token
    else:
        words=text.split()
    return words

# Assuming non_alpha_pattern is compiled outside the function



# Pre-compiled patterns and stemmer instances to improve efficiency
compiled_patterns = {}
stemmers = {}
stemmed_languages = ["arabic","danish","dutch","english","finnish","french","german","hungarian","italian","norwegian","portuguese","romanian","russian","spanish","swedish"]

def desp_preprocessing(text):
    try:
        language_code = detect(text)
        language_full_form = Language.get(language_code).language_name().lower()
    except:
        language_full_form = 'unknown'

    text = non_alpha_pattern.sub(" ", text)

    if language_full_form in stemmed_languages:
        stopwords_by_language = set(stopwords.words(language_full_form))
        
        if language_full_form not in compiled_patterns:
            pattern = r'\b(?:' + '|'.join(map(re.escape, stopwords_by_language)) + r')\b'
            compiled_patterns[language_full_form] = re.compile(pattern)
        
        text = compiled_patterns[language_full_form].sub(' ', text)
        
        if language_full_form not in stemmers:
            stemmers[language_full_form] = SnowballStemmer(language_full_form)
        stemmer = stemmers[language_full_form]
        
        words = [stemmer.stem(token) for token in text.split()]
    else:
        words = text.split()
    
    return words


def preprocess(text):
    text=non_alpha_pattern.sub(" ", text)
    return text
def create_index(row):
    id=row[0]
    text = ' '.join([str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6])])
    words=desp_preprocessing(text)
    for position, word in enumerate(words):
        if word not in positional_index:
            positional_index[word] = {'df': 0, 'posting_list': {}} #add the entry for the word if word is not contained
        if id not in positional_index[word]['posting_list']: #if it is the first appearence from the  word in the doc
            positional_index[word]['df'] += 1 #the df is incremented
            positional_index[word]['posting_list'][id] = [] #a list is created to store the positions
        # Append the position to the word's list for the document
        positional_index[word]['posting_list'][id].append(position)
        

connection = psycopg2.connect(
        host=hostname,
        dbname=database,
        user=username,
        password=password,
        port=port
    )
print("Loading jobs")
cursor = connection.cursor()
query=f"""
       SELECT Count(*) FROM jobs;

    """
cursor.execute(query)
N=cursor.fetchone()[0]
query=f"""
       SELECT * FROM jobs;

    """

cursor.execute(query)
with tqdm(total=N) as pbar:
    for row in cursor:
        create_index(row)
        pbar.update(1)

        # Update the progress bar by one for each row processed
        #pbar.update(1)

documents = [{"_id": k, **v} for k, v in positional_index.items()]



USERNAME= quote_plus('ttds')
PASSWORD = quote_plus('ttds')

uri = 'mongodb+srv://' + USERNAME + ':' + PASSWORD + "@ttds-cluster.vubotvd.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)



db=client.INDEX_DB
db['INDEX'].delete_many({})
db['INDEX'].insert_many(documents)