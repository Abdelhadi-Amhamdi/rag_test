import os
from google import genai
from dotenv import load_dotenv
from indexing.search import search

load_dotenv()


class RAGService:
	def __init__(self):
		self.client = genai.Client(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
		self.model = "models/gemini-2.5-flash"

	def get_system_prompt(self, client_name: str):
		return f"""You are an intelligent assistant for {client_name}, helping users find information from their insurance documents.

**Your role:**
- Be friendly and conversational for greetings and casual questions
- For factual questions about insurance/documents: Answer using ONLY the provided context documents
- Always cite the specific document source when providing factual information
- Be clear, concise, and professional
- Use the language of the user's question (French/English)

**How to respond:**

1. **Greetings/casual chat** (hello, hi, how are you, thank you, etc.):
   - Respond naturally and friendly
   - Ask how you can help them
   - No need to cite sources

2. **Factual questions about insurance/documents**:
   - Use ONLY the provided context documents
   - If the answer is NOT in the context, respond: "Je ne trouve pas cette information dans vos documents." or "I cannot find this information in your documents."
   - NEVER invent or make up information
   - NEVER use general knowledge about insurance
   - Always indicate which document your answer comes from
   - If context is ambiguous or incomplete, acknowledge this limitation

**Response format for factual questions:**
- Provide a clear, direct answer
- Reference the source document
- If multiple documents are relevant, cite all of them

Remember: Be conversational for greetings, but strict about using ONLY provided context for factual questions."""

	def build_prompt(self, query, context, client_name):
		return f"""Context documents for {client_name}:

		{context}

		---

		User question: {query}

		Answer based ONLY on the context above:"""

	def generate_answer(
		self,
		query: str,
		client_name: str,
		max_tokens: int = 1000
	) -> dict:
		
		try:
			search_results = search(query, client_name)
			
			if not search_results:
				return {
					"answer": "Je ne trouve pas d'information pertinente dans vos documents pour répondre à cette question.",
					"sources": [],
					"confidence": "none",
					"raw_results": []
				}
			
			context = self.format_context(search_results)
			
			
			system_prompt = self.get_system_prompt(client_name)
			user_prompt = self.build_prompt(query, context, client_name)
			
			response = self.client.models.generate_content(
				model=self.model,
				contents=[
					{"role": "user", "parts": [{"text": system_prompt}]},
					{"role": "model", "parts": [{"text": "Je comprends. Je répondrai uniquement en me basant sur les documents fournis."}]},
					{"role": "user", "parts": [{"text": user_prompt}]}
				],
				config={
					"temperature": 0.3,
					"max_output_tokens": max_tokens,
					"top_p": 0.80,
					"top_k": 10
				}
			)
			
			answer = response.text
			
			
			sources = [
				{
					"content": result["content"][:200] + "...",
					"metadata": result["metadata"],
					"similarity": round(1 - result["distance"], 4)
				}
				for result in search_results
			]
			
			return {
				"answer": answer,
				"sources": sources,
			}
			
		except Exception as e:
			raise


	def format_context(self, search_results) -> str:
		if not search_results:
			return "No relevant documents found."
		
		context_parts = []
		for i, result in enumerate(search_results, 1):
			similarity = round(1 - result['distance'], 4)
			context_parts.append(
				f"[Document {i}] (Relevance: {similarity})\n"
				f"Source: {result['metadata'].get('client', 'unknown')}\n"
				f"Content: {result['content']}\n"
			)
		
		return "\n".join(context_parts)

rag_service = RAGService()
