from langchain_chroma import Chroma
from llm_provider import get_embedding_model

CHROMA_DIR = "./chroma_db"


def retrieve_policy(query: str) -> str:
    embedding_model = get_embedding_model()

    vectordb = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_model,
    )

    retriever = vectordb.as_retriever(
        search_kwargs={"k": 4}
    )

    # New LangChain method
    docs = retriever.invoke(query)

    if not docs:
        return ""

    return "\n\n".join(doc.page_content for doc in docs)