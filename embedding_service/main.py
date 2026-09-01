from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI(title="Embedding Service")

# Allow CORS for the GUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model on CPU only
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: list[float]

@app.post("/embed", response_model=EmbedResponse)
def embed_text(request: EmbedRequest):
    embedding = model.encode(request.text).tolist()
    return EmbedResponse(embedding=embedding)

import requests
import uuid
import os

SOLR_URL = os.environ.get("SOLR_URL", "http://solr:8983/solr/semantic_search")

class InsertRequest(BaseModel):
    text: str

class InsertResponse(BaseModel):
    id: str
    message: str

@app.post("/insert", response_model=InsertResponse)
def insert_record(request: InsertRequest):
    embedding = model.encode(request.text).tolist()
    record_id = str(uuid.uuid4())
    doc = {
        "id": record_id,
        "text": request.text,
        "vector": embedding
    }
    res = requests.post(f"{SOLR_URL}/update?commit=true", json=[doc])
    res.raise_for_status()
    return InsertResponse(id=record_id, message="Record successfully inserted")

class SearchRequest(BaseModel):
    query: str
    result_count: str # "10", "20", or "all"

@app.post("/search")
def search_records(request: SearchRequest):
    # Determine topK
    top_k = 10
    if request.result_count.lower() == "all":
        count_res = requests.get(f"{SOLR_URL}/select?q=*:*&rows=0")
        count_res.raise_for_status()
        num_found = count_res.json()["response"]["numFound"]
        top_k = max(1, num_found)
    else:
        try:
            top_k = int(request.result_count)
        except ValueError:
            top_k = 10

    query_vector = model.encode(request.query).tolist()
    solr_query = f"{{!knn f=vector topK={top_k}}}[{','.join(map(str, query_vector))}]"
    
    res = requests.post(f"{SOLR_URL}/select", json={
        "query": solr_query,
        "fields": ["id", "text", "score"],
        "limit": top_k
    })
    res.raise_for_status()
    
    docs = res.json().get("response", {}).get("docs", [])
    
    # Process scores to true cosine similarity
    results = []
    total_score = 0
    for doc in docs:
        raw_score = doc.get("score", 0)
        true_cosine = (2 * raw_score) - 1
        total_score += true_cosine
        results.append({
            "id": doc.get("id"),
            "text": doc.get("text"),
            "similarity": true_cosine
        })
        
    combined_score = (total_score / len(docs)) if docs else 0.0
    
    return {
        "results": results,
        "combined_score": combined_score
    }

@app.delete("/clear")
def clear_database():
    res = requests.post(f"{SOLR_URL}/update?commit=true", json={"delete": {"query": "*:*"}})
    res.raise_for_status()
    return {"message": "Database cleared successfully"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
