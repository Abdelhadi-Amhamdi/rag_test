import streamlit as st
import requests

st.title("RAG Assistant")


client = st.selectbox("Select Client", ["Client A", "Client B"])
api_key = "tenantA_key" if client == "Client A" else "tenantB_key"

question = st.text_input("Ask a question:")


if st.button("Ask") and question:
	try:
		response = requests.post(
			"http://localhost:8000/chat",
			json={"message": question},
			headers={"X-API-KEY": api_key}
		)

		data = response.json()

		st.success(data["answer"]["answer"])

		st.write("**Sources:**")
		for source in data["answer"]["sources"]:
			st.text(source["content"][:150] + "...")

	except Exception as e:
		st.error(f"Error: {e}")