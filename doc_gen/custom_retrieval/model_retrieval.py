from doc_gen.open_ai.llm_retrival import generate_function_embedding, get_embeddings_llm
import requests
import json
import os

def publish_retrieval(function_name: str, contents: str):
    text = generate_function_embedding(contents)
    text = text.strip().lower()
    text = json.dumps({"sentences": text, "function_name": function_name, "code_itself": contents})
    r = requests.post(os.environ['TARGET_ENDPOINT_RAG'] + "/emb_save", data=text, headers={"Content-Type": "application/json"})
    if r.status_code != 200:
        raise Exception(f"{r.status_code}, {r.text}")

def get_retrieval(query: str):
    query = get_embeddings_llm(query=query)
    r = requests.get(f"{os.environ['TARGET_ENDPOINT_RAG']}/retrive", data=json.dumps({"phrase": query}), headers={"Content-Type": "application/json"})
    return r

def get_more_complex_retrival(query: str, answer: str = None):
    query = get_embeddings_llm(query=query)
    r = requests.get(f"{os.environ['TARGET_ENDPOINT_RAG']}/retrive", data=json.dumps({"phrase": query}), headers={"Content-Type": "application/json"})
    llm_final = get_embeddings_llm(query=query, answer=r.json())
    return llm_final
