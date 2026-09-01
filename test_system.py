import requests
import time
import sys
import statistics

API_URL = "http://localhost:8000"

def wait_for_services():
    print("Waiting for Embedding API Service...")
    for _ in range(60):
        try:
            res = requests.get(f"{API_URL}/health")
            if res.status_code == 200:
                print("API service is up!")
                break
        except requests.ConnectionError:
            pass
        time.sleep(2)
    else:
        print("API service failed to start.")
        sys.exit(1)

def test_system():
    wait_for_services()

    print("1. Testing Embedding Service (/embed) directly...")
    res = requests.post(f"{API_URL}/embed", json={"text": "test embedding"})
    assert res.status_code == 200
    vector = res.json()["embedding"]
    assert len(vector) == 384, "Embedding must be exactly 384 dimensions"
    print("Embedding service passed.")

    print("2. Testing Clear Database (/clear)...")
    res = requests.delete(f"{API_URL}/clear")
    assert res.status_code == 200
    print("Database cleared.")

    print("3. Testing Indexing (/insert)...")
    docs = [
        "machine learning applications in education",
        "artificial intelligence in the classroom",
        "recipes for baking chocolate chip cookies"
    ]

    for text in docs:
        res = requests.post(f"{API_URL}/insert", json={"text": text})
        assert res.status_code == 200, f"Failed to index: {res.text}"
        assert "id" in res.json()
    print("Indexing passed.")

    print("4. Testing KNN Search, Top N, and Similarity Scores (/search)...")
    query = "AI in schools"
    
    # Test Top 10
    res = requests.post(f"{API_URL}/search", json={
        "query": query,
        "result_count": "10"
    })
    
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 3, "Should return exactly 3 results (since only 3 exist)"
    
    # Check that scores are present and valid
    scores = [doc["similarity"] for doc in data["results"]]
    assert all(-1.0 <= s <= 1.0 for s in scores), "True cosine scores should be -1 to 1"
    
    combined_score = data["combined_score"]
    print(f"Top 10 passed. Combined true cosine score: {combined_score:.3f}")

    # Test All
    res_all = requests.post(f"{API_URL}/search", json={
        "query": query,
        "result_count": "all"
    })
    data_all = res_all.json()
    assert len(data_all["results"]) == 3, "All should return all 3 results"
    print(f"'All' logic passed. Retrieved {len(data_all['results'])} records.")

    print("5. Testing Final Clear Database (/clear)...")
    res = requests.delete(f"{API_URL}/clear")
    assert res.status_code == 200

    # Verify empty by searching again
    res = requests.post(f"{API_URL}/search", json={"query": "test", "result_count": "all"})
    assert len(res.json()["results"]) == 0, "Database should be empty"
    print("Clear Database passed.")

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_system()
