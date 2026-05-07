import os
import requests
from functools import lru_cache
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from langchain_core.messages import AIMessage

load_dotenv()


# -------------------------------------------------------------------
# Custom Embedding class
# -------------------------------------------------------------------
class AzureEmbeddingViaRequests:
    def __init__(self):
        print("🔹 Initializing AzureEmbeddingViaRequests...")

        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.embedding_endpoint = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")

        print("🔹 API Version:", self.api_version)
        print("🔹 Embedding Endpoint:", self.embedding_endpoint)

        if not self.embedding_endpoint or not self.api_key:
            raise ValueError("❌ Embedding endpoint or API key missing")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
        }

        print("✅ AzureEmbeddingViaRequests initialized successfully")

    def embed_query(self, text: str) -> list[float]:
        print("\n▶ embed_query called")
        print("▶ Input text:", text)

        payload = {"input": text}
        url = f"{self.embedding_endpoint}?api-version={self.api_version}"

        print("▶ POST URL:", url)

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        print("▶ Status Code:", response.status_code)

        if response.status_code != 200:
            print("❌ Raw embedding response:", response.text)
            raise RuntimeError(
                f"Embedding failed ({response.status_code}): {response.text}"
            )

        data = response.json()
        vector = data["data"][0]["embedding"]

        print("✅ Embedding success")
        print("✅ Dimensions:", len(vector))
        print("✅ First 5 values:", [round(v, 6) for v in vector[:5]])

        return vector

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        print("\n▶ embed_documents called")
        print("▶ Number of documents:", len(texts))

        return [self.embed_query(text) for text in texts]


# -------------------------------------------------------------------
# Custom Chat LLM class compatible with LangChain chains
# -------------------------------------------------------------------
class AzureChatViaRequests(Runnable):
    def __init__(self, temperature: float = 0.0):
        print("🔹 Initializing AzureChatViaRequests...")

        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.chat_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.temperature = temperature

        print("🔹 API Version:", self.api_version)
        print("🔹 Chat Endpoint:", self.chat_endpoint)

        if not self.chat_endpoint or not self.api_key:
            raise ValueError("❌ Chat endpoint or API key missing")

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
        }

        print("✅ AzureChatViaRequests initialized successfully")

    def _convert_input_to_messages(self, input_data):
        if isinstance(input_data, str):
            return [{"role": "user", "content": input_data}]

        if hasattr(input_data, "to_messages"):
            input_data = input_data.to_messages()

        if isinstance(input_data, list):
            messages = []

            for msg in input_data:
                role = "user"

                if hasattr(msg, "type"):
                    if msg.type == "system":
                        role = "system"
                    elif msg.type == "human":
                        role = "user"
                    elif msg.type == "ai":
                        role = "assistant"

                content = msg.content if hasattr(msg, "content") else str(msg)

                messages.append({
                    "role": role,
                    "content": content,
                })

            return messages

        return [{"role": "user", "content": str(input_data)}]

    def invoke(self, input, config=None, **kwargs):
        print("\n▶ chat invoke called")

        url = f"{self.chat_endpoint}?api-version={self.api_version}"
        messages = self._convert_input_to_messages(input)

        payload = {
            "messages": messages,
            "temperature": self.temperature,
        }

        print("▶ POST URL:", url)

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        print("▶ Chat Status Code:", response.status_code)

        if response.status_code != 200:
            print("❌ Raw chat response:", response.text)
            raise RuntimeError(
                f"Chat failed ({response.status_code}): {response.text}"
            )

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        print("✅ Chat success")
        print("✅ Reply:", content)

        return AIMessage(content=content)


# -------------------------------------------------------------------
# Public factory for embeddings
# -------------------------------------------------------------------
def get_embedding_model():
    print("============================================================")

    provider = os.getenv("LLM_PROVIDER", "").lower()
    print("🔹 LLM_PROVIDER:", provider)

    if provider != "azure_openai":
        raise ValueError(f"❌ Unsupported LLM_PROVIDER: {provider}")

    print("✅ Returning AzureEmbeddingViaRequests instance")
    return AzureEmbeddingViaRequests()


# -------------------------------------------------------------------
# Public factory for chat LLM
# -------------------------------------------------------------------
@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.0):
    print("\n🔹 get_llm() called")
    print("🔹 Temperature:", temperature)

    provider = os.getenv("LLM_PROVIDER", "").lower()
    print("🔹 LLM_PROVIDER:", provider)

    if provider == "azure_openai":
        print("✅ Returning AzureChatViaRequests instance")
        return AzureChatViaRequests(temperature=temperature)

    print("⚠️ Falling back to OpenAI public API")
    return ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=temperature,
    )