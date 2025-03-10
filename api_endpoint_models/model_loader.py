from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F
import torch
from torch import Tensor
import logging

FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

logging.info("Carregando modelo")

device = torch.device("cuda")

path = r"api_endpoint_models\models\paraphrase-multilingual-MiniLM-L12-v2"

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

tokenizer = AutoTokenizer.from_pretrained(path)
model = AutoModel.from_pretrained(path)
model.to(device)

logging.info("Modelo carregado")

def run_model(sentences) -> Tensor:
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
    encoded_input = encoded_input.to(device)
    model_output = model(**encoded_input)
    sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    return sentence_embeddings

def retrivel_model(emb1: str, emb2: list[float]):
    if not isinstance(emb1, torch.Tensor):
        emb1: Tensor = torch.tensor(emb1)
    if not isinstance(emb2, torch.Tensor):
        emb2: Tensor = torch.tensor(emb2)
    emb1 = emb1.to(device)
    emb2 = emb2.to(device)
    if emb1.ndim == 1:
        emb1 = emb1.unsqueeze(0)
    if emb2.ndim == 1:
        emb2 = emb2.unsqueeze(0)

    return F.cosine_similarity(emb1, emb2).item()