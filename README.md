# Semantic Search Project

A clean, reproducible semantic search system using Apache Solr and `sentence-transformers/all-MiniLM-L6-v2`.

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
