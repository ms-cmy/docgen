from openai import OpenAI
import os


API_KEY = os.environ['TOKEN']
GCP_MODEL = os.environ['GOOGLE_MODEL']

client = OpenAI(
    api_key=os.environ['TOKEN'],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

class AgentDoc:
    def __init__(self, path: str):
        self.path = path
    
    def call_LLM(self):
        pass