import re
import os
import numpy
from google import genai
from dotenv import load_dotenv


load_dotenv()


def semantic_chunking(text, max_sentences=3):

	sentences = re.split(r'(?<=[.!?])\s+', text.strip())

	chunks = []
	for i in range(0, len(sentences), max_sentences):
		chunk = " ".join(sentences[i : i + max_sentences]).strip()
		chunks.append(chunk)

	return chunks


def create_embeddings(chunks : [str]):

	client = genai.Client(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))

	response = client.models.embed_content(
		model="gemini-embedding-001",
		contents=chunks
	)
	
	embeddings = [emb.values for emb in response.embeddings]
	embeddings = numpy.array(embeddings).astype("float32")

	norms = numpy.linalg.norm(embeddings, axis=1, keepdims=True)
	embeddings = embeddings / norms

	return embeddings


