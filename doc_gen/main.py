# import requests
# import json
# import dotenv
# from typing import Union
# import os


# dotenv.load_dotenv()

# URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/{model}"
# TOKEN = os.environ['TOKEN']

# def format_phrases(phrases: list[str]) -> str:
#     final_value = {"inputs": {"sentences": phrases}}
#     return json.dumps(final_value)

# def rag_request(phrases: Union[list[str]],
#                 model: str = "paraphrase-multilingual-MiniLM-L12-v2") -> requests.Response:
#     if isinstance(phrases, str):
#         phrases = [phrases]
#     r = requests.post(URL.format(model=model),
#                       headers={
#                           "Content-Type": "application/json",
#                           f"Authorization": "Bearer {TOKEN}"},
#                       data=format_phrases(phrases))
    
#     if r.status_code != 200:
#         print(r.text)
#         raise Exception("deu merda")
#     return r