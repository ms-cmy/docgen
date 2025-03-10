from model_loader import run_model, retrivel_model
from db_connect import insert_document, get_similarity, check_if_exists
from flask import Flask, request
import json
import logging
import time

app = Flask(__name__)

FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

logger.info("startig application")

MODEL_PATH = r"api_endpoint_models\models\paraphrase-multilingual-MiniLM-L12-v2"

@app.route("/health")
def health():
    logger.info("Health Status called")
    return ("OK \n", 200)

@app.route("/rag", methods=['POST'])
def rag():
    result = request.json
    sentences = result.get("sentences")
    if sentences is None:
        return ("please pass the senteses in str or list[str] format", 400)
    embeddings = run_model(sentences)
    return (embeddings.tolist(), 200)

@app.route("/emb_save", methods=['POST'])
def generate_and_save_emb():
    start = time.perf_counter()
    logger.info("Emb save começou")
    result = request.json
    sentences = result.get("sentences")
    function_name = result.get("function_name")
    code_itself = result.get("code_itself")
    if sentences is None:
        return ("please pass the senteses in str or list[str] format", 400)
    embeddings = run_model(sentences)
    with open(r"C:\Estudos\vstl32ol\api_endpoint_models\embedded_storage\emb.jsonl", "a") as f:
        for i, phrase in zip(embeddings, [sentences]):
            f.writelines(json.dumps({function_name: i.tolist(), "code": code_itself}) + "\n")
    end = time.perf_counter()
    ms = round(end - start, 2)
    logger.info(f"generate_and_save_emb ms response: {ms}")
    return ("Done + \n", 200)

@app.route("/retrive", methods=['GET'])
def retrive():
    start = time.perf_counter()
    result=request.json
    phrase = result.get("phrase", None)
    if phrase is None:
        return ("kd phrase????", 400)
    phrase_emb = run_model(phrase).tolist()
    data = []
    with open(r"C:\Estudos\vstl32ol\api_endpoint_models\embedded_storage\emb.jsonl", "r") as f:
        for i in f.readlines():
            data.append(json.loads(i))
    response_dict = {}
    for i in data:
        for key, value in i.items():
            if key == "code":
                response_dict[old_key].append(value)
                continue
            res = retrivel_model(phrase_emb, value)
            response_dict[key] = [round(res, 2)]
            old_key = key
    end = time.perf_counter()
    ms = round(end - start, 3)
    logger.info(f"generate_and_save_emb ms response: {ms}")
    return (response_dict, 200)

@app.route("/to_bd", methods=['POST'])
def send_to_banco():
    start = time.perf_counter()
    logger.info("Emb save no sql começou")
    result = request.json
    sentences = result.get("sentences")
    function_name = result.get("function_name")
    code_itself = result.get("code_itself")
    if check_if_exists(function_name):
        end = time.perf_counter()
        ms = round(end - start, 2)
        logger.info(f"send_to_banco ms response: {ms}, already exist, finishing early")
        return ("Finishing early, already exists", 200)
    if sentences is None:
        return ("please pass the senteses in str or list[str] format", 400)
    if code_itself is None:
        return ("cade o code_itself", 400)
    embeddings = run_model(sentences).tolist()[0]
    insert_document(data={"function_name": function_name,
                          "embed": embeddings,
                          "text_that_got_embed": sentences,
                          "source_code": code_itself})
    end = time.perf_counter()
    ms = round(end - start, 2)
    logger.info(f"send_to_banco ms response: {ms}")
    return ("Banco updated \n", 200)

@app.route("/retrive_from_banco", methods=['GET'])
def retrive_from_banco():
    start = time.perf_counter()
    result=request.json
    phrase = result.get("phrase", None)
    if phrase is None:
        return ("kd phrase????", 400)
    phrase_emb = run_model(phrase).tolist()[0]
    response_dict = get_similarity(phrase_emb)
    end = time.perf_counter()
    ms = round(end - start, 3)
    logger.info(f"generate_and_save_emb ms response: {ms}")
    return (response_dict, 200)