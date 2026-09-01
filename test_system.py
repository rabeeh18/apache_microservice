import requests
import time
import sys
import statistics

EMBED_URL = "http://localhost:8000"
SOLR_URL = "http://localhost:8983/solr/semantic_search"

def wait_for_services():
    print("Waiting for Embedding Service...")
    for _ in range(30):
        try:
            res = requests.get(f"{EMBED_URL}/health")
            if res.status_code == 200:
                print("Embedding service is up!")
                break
        except requests.ConnectionError:
            pass
        time.sleep(2)
    else:
        print("Embedding service failed to start.")
        sys.exit(1)

    print("Waiting for Solr Service and Schema...")
    for _ in range(60):
        try:
            res = requests.get(f"{SOLR_URL}/schema")
            if res.status_code == 200 and "knn_vector" in res.text:
                print("Solr and schema are ready!")
                break
        except requests.ConnectionError:
            pass
        time.sleep(2)
    else:
        print("Solr service/schema failed to initialize.")
        sys.exit(1)

def embed_text(text):
    res = requests.post(f"{EMBED_URL}/embed", json={"text": text})
    assert res.status_code == 200
    vector = res.json()["embedding"]
    assert len(vector) == 384, "Embedding must be exactly 384 dimensions"
    return vector

def test_system():
    wait_for_services()

    print("1. Testing Embedding Service (384-dimensional output)...")
    docs = [
        {"id": "doc1", "text": "machine learning applications in education"},
        {"id": "doc2", "text": "artificial intelligence in the classroom"},
        {"id": "doc3", "text": "recipes for baking chocolate chip cookies"}
    ]

    for doc in docs:
        doc["vector"] = embed_text(doc["text"])
    
    print("Embedding service passed.")

    print("2. Testing Solr Connectivity and Indexing...")
    # Clear first just in case
    requests.post(f"{SOLR_URL}/update?commit=true", json={"delete": {"query": "*:*"}})
    
    res = requests.post(f"{SOLR_URL}/update?commit=true", json=docs)
    assert res.status_code == 200, f"Failed to index: {res.text}"
    print("Indexing passed.")

    print("3. Testing KNN Search, Top N, and Similarity Scores...")
    query = "AI in schools"
    query_vector = embed_text(query)

    # Test Top 2
    solr_query = f"{{!knn f=vector topK=2}}{query_vector}"
    res = requests.post(f"{SOLR_URL}/select", json={
        "query": solr_query,
        "fields": ["id", "text", "score"],
        "limit": 2
    })
    
    assert res.status_code == 200
    data = res.json()
    assert len(data["response"]["docs"]) == 2, "Should return exactly 2 results"
    
    # Check that scores are present and valid
    scores = [doc["score"] for doc in data["response"]["docs"]]
    assert all(0 <= s <= 2 for s in scores), "Scores should be normalized cosine (0-1 approx)"
    
    # Calculate combined score
    combined_score = sum(scores) / len(scores)
    print(f"Top 2 passed. Combined score: {combined_score:.3f}")

    print("4. Testing Clear Database...")
    res = requests.post(f"{SOLR_URL}/update?commit=true", json={"delete": {"query": "*:*"}})
    assert res.status_code == 200

    # Verify empty
    res = requests.get(f"{SOLR_URL}/select?q=*:*")
    assert res.json()["response"]["numFound"] == 0, "Database should be empty"
    print("Clear Database passed.")

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_system()
