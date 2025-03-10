from doc_gen.open_ai.llm_retrival import generate_function_embedding, get_embeddings_llm
import logging
import requests
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def db_retrieval(query, return_human=False):
    logger.info(f"buscando no banco com a seguinte query: {query}")
    r = requests.get(f"{os.environ['TARGET_ENDPOINT_RAG']}/retrive_from_banco", data=json.dumps({"phrase": query}), headers={"Content-Type": "application/json"})
    if return_human==True:
        return r.json()
    return r

def publish_retrieval(function_name: str, contents: str):
    text = generate_function_embedding(contents)
    text = text.strip().lower()
    text = json.dumps({"sentences": text, "function_name": function_name, "code_itself": contents})
    r = requests.post(os.environ['TARGET_ENDPOINT_RAG'] + "/to_bd", data=text, headers={"Content-Type": "application/json"})
    if r.status_code != 200:
        raise Exception(f"{r.status_code}, {r.text}")

def get_retrieval(query: str):
    query = get_embeddings_llm(query=query)
    r = db_retrieval(query)
    return r

def get_more_complex_retrival(query: str):
    query = get_embeddings_llm(query=query)
    r = db_retrieval(query)
    llm_final = get_embeddings_llm(query=query, answer=r.json())
    return llm_final
