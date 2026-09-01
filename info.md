# Semantic Search System Documentation

## Overall Architecture
The system consists of three main services orchestrated via Docker Compose:
1. **GUI (Frontend Proxy)**: An Nginx container serving a static HTML/JS frontend and acting as a reverse proxy to route `/api/embed` to the Embedding Service and `/api/solr/` to Apache Solr. This avoids CORS issues and keeps all communication within the Docker network.
2. **Embedding Service**: A Python FastAPI application that loads the `sentence-transformers/all-MiniLM-L6-v2` model to convert text strings into 384-dimensional dense vectors.
3. **Apache Solr**: The search engine storing records and performing KNN (K-Nearest Neighbors) semantic search over the vector field.

## Embedding Service and Model
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Output**: 384-dimensional embeddings.
- **API Endpoint**: `POST /embed` (Accepts `{"text": "..."}`, returns `{"embedding": [...]}`).
- This exact model is used consistently for indexing records and embedding search queries.

## Apache Solr and KNN Vector Search
- **Version**: Official Solr 9 Docker image.
- **Field Configuration**: A `knn_vector` field with `vectorDimension=384` and `similarityFunction=cosine`.
- **Exposed API**: Solr is exposed directly to the host machine on port `8983`. You can access the Solr Admin UI at `http://localhost:8983`.
- **Search**: The KNN search (`{!knn f=vector topK=...}[...]`) calculates semantic similarity in the vector space.

## Graphical User Interface (GUI)
- **Top 10 / Top 20 / All**: Allows the user to select how many results to retrieve.
- **Text Preview**: Clicking "Show Preview" displays the stored text associated with the retrieved record.
- **Clear Database**: Allows wiping the index without dropping the collection structure. This keeps the schema intact for future insertions.

## Similarity Scores
- **Individual Similarity Score**: For vector fields using the `cosine` similarity metric, Solr returns a normalized score calculated as `(1 + true_cosine_similarity) / 2`. To display the standard mathematical True Cosine Similarity (which ranges from -1.0 to 1.0, where 1.0 is identical), the GUI recalculates this using the exact formula: `True Cosine Similarity = (2 * Solr_Score) - 1`. This value is directly displayed for each result.
- **Combined Similarity Score**: This is calculated as the arithmetic mean of the individual true cosine similarity scores of the returned results. If "Top 10" is selected, it averages the top 10 scores. If "All" is selected, it calculates the mean across every document retrieved. This gives an overall indicator of how well the result set matches the query.

## How to Start the System
```bash
docker compose up --build -d
```

## How to Access Services
- **GUI**: `http://localhost:8080`
- **Solr Admin UI / API**: `http://localhost:8983`
- **Embedding Service API**: `http://localhost:8000/embed` (also accessible via GUI proxy at `http://localhost:8080/api/embed`)

## Example API Calls

### 1. Embed Text
```bash
curl -X POST -H "Content-Type: application/json" -d '{"text": "machine learning"}' http://localhost:8000/embed
```

### 2. Index a Document in Solr
```bash
curl -X POST -H "Content-Type: application/json" -d '[
  {
    "id": "doc1",
    "text": "machine learning applications in education",
    "vector": [0.1, 0.2, ... 384 values]
  }
]' http://localhost:8983/solr/semantic_search/update?commit=true
```

### 3. Perform a Search directly via Solr
```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "query": "{!knn f=vector topK=10}[0.1, 0.2, ... 384 values]",
  "fields": ["id", "score"]
}' http://localhost:8983/solr/semantic_search/select
```
