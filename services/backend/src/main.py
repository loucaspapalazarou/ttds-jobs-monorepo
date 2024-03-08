from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# NEW
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return "Hello, World!"


@app.get("/search/{query}")
def search(query: str):
    return {
        "query": query,
        "results": [
            {'id': 1, 'title': 'Developer, World!', 'description': 'Description text.'},
            {'id': 2,'title': 'Hello, World!', 'description': 'Description text.'},
            {'id': 3,'title': 'Hello, World!', 'description': 'Description text.'},
            {'id': 4,'title': 'Hello, World!', 'description': 'Description text.'},
            {'id': 5,'title': 'Hello, World!', 'description': 'Description text.'},
            {'id': 6,'title': 'Hello, World!', 'description': 'Description text.'},
            {'id': 7,'title': 'Hello, World!', 'description': 'Description text.'},
            {'id': 8,'title': 'Hello, World!', 'description': 'Description text.'},
            {'id': 9,'title': 'Hello, World!', 'description': 'Description text.'},
            {'id': 10,'title': 'Hello, World!', 'description': 'Description text.'},
        ]
    }