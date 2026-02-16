import chromadb
from pathlib import Path
from utils import semantic_chunking, create_embeddings
import uuid

def build_index(text : str, client_name : str, collection, client_instance):
	
	chunks = semantic_chunking(text, 3)
	embeddings = create_embeddings(chunks)
	
	collection.add(
		documents=chunks,
		embeddings=embeddings,
		ids=[str(uuid.uuid4()) for _ in chunks],
		metadatas=[{"client": client_name} for _ in chunks]
	)


def index_all_docs(base_folder: str, collection, client_instance):
	base_path = Path(base_folder)

	txt_files = list(base_path.rglob("*.txt"))

	print(f"Found {len(txt_files)} documents to index.")

	for file_path in txt_files:
		with open(file_path, "r", encoding="utf-8") as f:
			content = f.read()

		client_name = file_path.parent.name
		print(client_name)

		build_index(content, client_name, collection, client_instance)
		print(f"Indexed {file_path} for client '{client_name}'\n--------------\n")

if __name__ == "__main__":
	client = chromadb.PersistentClient(path="../vector_store/chroma_db")

	print("create collection")

	collection = collection = client.get_or_create_collection(
		name="clients_docs",
		embedding_function=None,
		metadata={"distance_metric": "cosine"}
	)

	print("Start indexing documents...")
	index_all_docs("../documents", collection, client)
