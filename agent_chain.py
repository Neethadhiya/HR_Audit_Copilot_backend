from rag_tool import retrieve_policy
from google_search_tool import google_search
from llm_provider import get_llm

llm = get_llm()


def is_rag_insufficient(answer: str, context: str) -> bool:
    if not context or not context.strip():
        return True

    if not answer or not answer.strip():
        return True

    weak_signals = [
        "UNKNOWN",
        "insufficient",
        "not mentioned",
        "not provided",
        "does not specify",
        "cannot determine",
    ]

    answer_lower = answer.lower()

    return any(signal.lower() in answer_lower for signal in weak_signals)


def answer_from_context(query: str, context: str, source_name: str) -> str:
    prompt = f"""
You are an HR audit assistant.

Answer the question using ONLY the context below.

Rules:
- If the context is insufficient, answer exactly: UNKNOWN
- Do not guess
- Keep the answer concise
- Do not mention documents, uploads, or files

Source:
{source_name}

Context:
{context}

Question:
{query}

Answer:
"""

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        return response.content.strip()

    return str(response).strip()


def run_agent(query: str):
    # 1. Try RAG first
    rag_context = retrieve_policy(query)
    rag_answer = answer_from_context(
        query=query,
        context=rag_context,
        source_name="RAG"
    )

    if not is_rag_insufficient(rag_answer, rag_context):
        return {
            "answer": rag_answer,
            "source_used": "rag",
            "confidence": 0.87
        }

    # 2. Fallback to Google Search
    google_context = google_search(query)
    google_answer = answer_from_context(
        query=query,
        context=google_context,
        source_name="Google Search"
    )

    if not is_rag_insufficient(google_answer, google_context):
        return {
            "answer": google_answer,
            "source_used": "google_search",
            "confidence": 0.65
        }

    # 3. If both fail
    return {
        "answer": "UNKNOWN",
        "source_used": "none",
        "confidence": 0.0
    }