from langchain_community.vectorstores import Chroma
from llm_provider import get_embedding_model

VECTOR_DB_DIR = "chroma_db"

embedding = get_embedding_model()

vectordb = Chroma(
    persist_directory=VECTOR_DB_DIR,
    embedding_function=embedding
)

collection = vectordb._collection

print("\n✅ Total document chunks stored in ChromaDB:\n")
print(collection.count())