import chromadb
from .utils import create_embeddings
from pathlib import Path


def search(query: str, clientName):
	PROJECT_ROOT = Path(__file__).parent.parent.resolve()
	CHROMA_DB_PATH = PROJECT_ROOT / "vector_store" / "chroma_db"
	client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
	collection = client.get_collection(name="clients_docs")
	query_embedding = create_embeddings([query])[0]


	results = collection.query(
		query_embeddings=[query_embedding],
		where={"client": clientName},
		n_results=4
	)

	result = []
	for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
		result.append({
			"content" : doc,
			"metadata" : meta,
			"distance" : dist
		})
	
	return result

