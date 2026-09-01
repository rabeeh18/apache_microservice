
## Setup Instructions

1. Ensure **Docker** and **Docker Compose** are installed and running.
2. Clone this repository (or navigate to this directory).
3. Start the system:
   ```bash
   docker compose up --build -d
   ```
4. Wait a moment for the models to load and Solr to initialize.
5. Open the GUI at: `http://localhost:8080`
6. You can access the Solr Admin UI directly at: `http://localhost:8983`

## Usage

1. **Open the GUI**.
2. **Enter a semantic query** (e.g., "machine learning applications").
3. Select **Top 10, Top 20, or All**.
4. Click **Search**.
5. View individual similarity scores and the combined semantic similarity score.
6. Click **Show Preview** on any result to see the full text.

For more detailed architectural information, please see `info.md`.

## Public API Endpoints

The Embedding Service (running on port `8000`) exposes a complete backend API that integrates with Solr. The GUI uses these exact endpoints.

### 1. Insert a Record
**URL:** `http://localhost:8000/insert`
**Method:** `POST`
**Description:** Accepts a text string, automatically generates its 384-dimensional embedding using the CPU model, and stores both the text and vector in Solr.
**Request Format:** `{"text": "your text here"}`
**Response Format:** `{"id": "uuid-of-record", "message": "Record successfully inserted"}`
**Example:**
```bash
curl -X POST -H "Content-Type: application/json" -d '{"text": "machine learning"}' http://localhost:8000/insert
```

### 2. Search Records
**URL:** `http://localhost:8000/search`
**Method:** `POST`
**Description:** Accepts a query string and desired result count ("10", "20", or "all"). Automatically embeds the query, performs KNN semantic search in Solr, and returns the ranked records with mathematically exact True Cosine Similarities alongside a combined mean score.
**Request Format:** `{"query": "your query", "result_count": "10"}`
**Response Format:** `{"results": [{"id": "...", "text": "...", "similarity": 0.85}], "combined_score": 0.85}`
**Example:**
```bash
curl -X POST -H "Content-Type: application/json" -d '{"query": "machine learning", "result_count": "10"}' http://localhost:8000/search
```

### 3. Clear Database
**URL:** `http://localhost:8000/clear`
**Method:** `DELETE`
**Description:** Deletes all indexed records from the Solr collection, effectively emptying the database while preserving the schema and vector configurations for future use.
**Request Format:** No body required.
**Response Format:** `{"message": "Database cleared successfully"}`
**Example:**
```bash
curl -X DELETE http://localhost:8000/clear
```
