import os
import requests
from dotenv import load_dotenv

load_dotenv()

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value

def main():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    # ✅ Since endpoint already contains full path, just append version
    url = f"{endpoint}?api-version={api_version}"

    # ✅ REQUIRED headers for your proxy
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-API-Key": api_key
    }

    payload = {
        "messages": [
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": "say hello..why python in 2 sentence "}
        ],
        "temperature": 0,
        
    }

    print("▶ Sending request...")
    print("▶ URL:", url)

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print("▶ Status Code:", response.status_code)
        print("▶ Raw Response:")
        print(response.text)

        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            print("\n✅ SUCCESS")
            print("Model reply:", reply)
        else:
            print("\n❌ FAILED")

    except Exception as e:
        print("\n❌ ERROR:", str(e))
    #     # ---------------- EMBEDDINGS TEST ----------------
    # # Replace chat/completions with embeddings
    # chat_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT").rstrip("/")
    # chat_url = f"{chat_endpoint}?api-version={api_version}"
    # embedding_endpoint = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
    # embedding_url = f"{embedding_endpoint}?api-version={api_version}"

    # embedding_payload = {
    #     "input": "IPO immediate testing sentence for embeddings"
    # }

    # print("\n=== Embeddings test ===")
    # print("▶ Embedding URL:", embedding_url)

    # try:
    #     embedding_response = requests.post(
    #         embedding_url,
    #         headers=headers,
    #         json=embedding_payload,
    #         timeout=30
    #     )

    #     print("▶ Embedding Status Code:", embedding_response.status_code)
    #     print("▶ Embedding Raw Response:")
    #     print(embedding_response.text[:500])

    #     if embedding_response.status_code == 200:
    #         embedding_data = embedding_response.json()
    #         vector = embedding_data["data"][0]["embedding"]

    #         print("\n✅ EMBEDDING SUCCESS")
    #         print("Input text:", embedding_payload["input"])
    #         print("Embedding dimensions:", len(vector))
    #         print("First 5 values:", [round(v, 6) for v in vector[:5]])
    #     else:
    #         print("\n❌ EMBEDDING FAILED")
    #         print("Likely reason: current deployment does not support embeddings.")
    #         print("You may need a separate embedding deployment.")

    # except Exception as e:
    #     print("\n❌ EMBEDDING ERROR:", str(e))

if __name__ == "__main__":
    main()