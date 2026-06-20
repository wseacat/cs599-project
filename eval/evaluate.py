"""Simple RAG evaluation script - checks if golden answers appear in generated response."""
import json
import requests
import time

API_URL = "http://localhost:8002/api/chat"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzIiwiZXhwIjoxNzgxNjY4NTk0fQ.pGS0Bqyw1a9B7xjttqJQq6UdStvv0OWepFmzYkC35vg"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def evaluate():
    with open("eval/test_set.jsonl", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f]

    results = []
    for case in cases:
        q = case["question"]
        golden = case["golden_answers"]
        t0 = time.time()
        try:
            resp = requests.post(API_URL, headers=HEADERS, json={"message": q}, timeout=180)
            answer = resp.json().get("answer", "")
        except Exception as e:
            answer = f"ERROR: {e}"
        elapsed = time.time() - t0

        # Check if any golden answer appears in the response
        hits = [g for g in golden if g.lower() in answer.lower()]
        hit = len(hits) > 0
        results.append({"id": case["id"], "question": q, "hit": hit, "hits": hits, "time": f"{elapsed:.1f}s"})
        status = "PASS" if hit else "FAIL"
        print(f"[{status}] Q{case['id']}: {q[:40]}... ({elapsed:.1f}s) hits={hits}")

    total = len(results)
    passed = sum(1 for r in results if r["hit"])
    print(f"\n=== Results: {passed}/{total} ({passed/total*100:.0f}%) ===")
    return results

if __name__ == "__main__":
    evaluate()
