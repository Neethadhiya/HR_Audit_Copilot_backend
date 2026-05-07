import os
import requests


def google_search(query: str) -> str:
    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    cx = os.getenv("GOOGLE_SEARCH_CX")

    if not api_key or not cx:
        return "UNKNOWN"

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": 5,
    }

    response = requests.get(url, params=params, timeout=20)

    if response.status_code != 200:
        print("❌ Google Search failed:", response.status_code, response.text)
        return "UNKNOWN"

    data = response.json()
    items = data.get("items", [])

    if not items:
        return "UNKNOWN"

    results = []

    for item in items:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")

        results.append(
            f"Title: {title}\nSnippet: {snippet}\nURL: {link}"
        )

    return "\n\n".join(results)