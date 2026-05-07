from llm_provider import get_embedding_model

embedding_model = get_embedding_model()

vector = embedding_model.embed_query("test embedding")
print("Vector length:", len(vector))
print("First 5 values:", vector[:5])