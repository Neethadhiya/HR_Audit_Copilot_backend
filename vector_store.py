import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from llm_provider import get_embedding_model
from dotenv import load_dotenv
load_dotenv()
# ─────────────────────────────────────────────
# Vector DB configuration
# ─────────────────────────────────────────────

VECTOR_DB_DIR = os.path.abspath("chroma_db")
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

# ✅ Create embedding model ONCE (important)
embedding_model = get_embedding_model()

# ─────────────────────────────────────────────
# Ingest HR Policy
# ─────────────────────────────────────────────

def ingest_hr_policy(file_path: str):
    """
    Loads a PDF or DOCX HR policy file, splits it into chunks,
    embeds the chunks using Azure OpenAI, and stores them in Chroma.
    """

    _, ext = os.path.splitext(file_path.lower())

    # ✅ Load document
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = UnstructuredWordDocumentLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX allowed.")

    docs = loader.load()
    print("📄 Documents loaded:", len(docs))

    # ✅ Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)
    print("✂️ Chunks created:", len(chunks))

    if not chunks:
        raise ValueError("No text chunks generated from document")

    # ✅ Load or create Chroma collection
    vectordb = Chroma(
        collection_name="hr_policy",
        embedding_function=embedding_model,
        # persist_directory=VECTOR_DB_DIR
    )

    # ✅ Add documents (embeddings created automatically)
    vectordb.add_documents(chunks)
    print("77777777777777777777777777")
    print("vectordb._collection.count",vectordb._collection.count())
    total_vectors = vectordb._collection.count()
    print("88888888888888888888888888888888888")
    print("✅ Total vectors stored:", total_vectors)
    print("99999999999999999999999999999999999999999")
    return vectordb