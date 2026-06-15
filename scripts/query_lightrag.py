import os
import json
import requests

BASE_URL = os.getenv("LIGHTRAG_URL", "http://localhost:9621")
API_KEY = os.getenv("LIGHTRAG_API_KEY", "")


def query_lightrag(question: str, mode: str = "mix") -> dict:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    payload = {
        "query": question,
        "mode": mode,
        "include_references": True,
        "include_chunk_content": True,
        "enable_rerank": False,
    }
    response = requests.post(f"{BASE_URL}/query", headers=headers, json=payload, timeout=240)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "請整理主要架構"
    print(json.dumps(query_lightrag(q), ensure_ascii=False, indent=2))
