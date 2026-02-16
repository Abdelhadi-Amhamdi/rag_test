from fastapi import FastAPI, Request
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from fastapi.responses import JSONResponse
from indexing.search import search
from rag_service import rag_service

class ChatRequestBody(BaseModel):
	message : str

load_dotenv()

API_KEYS = {
	os.getenv("clientA", "") : "tenantA",
	os.getenv("clientB", "") : "tenantB"
}

app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):

	api_key = request.headers.get("X-API-KEY")
	client = API_KEYS.get(api_key, '')
	
	if not api_key or not client:
		return JSONResponse({"error": "Unauthorized. Invalid X-API-KEY"}, status_code=401)
	request.state.client = client
	response = await call_next(request)
	return response


@app.post('/chat')
async def chat(request: Request, body: ChatRequestBody):
	client_name = getattr(request.state, "client", None)
	query = body.message
	answer = rag_service.generate_answer(query, client_name)
	return {"answer" : answer}


