from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from itertools import chain
import datetime
import yaml
import logging
import os
import json

FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

def list_files_recursively_os_walk(folder_path):
    file_list = []
    if not os.path.isdir(folder_path):
        raise Exception("xd")
    
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            file_list.append(full_path)
    return file_list

class DocGen:
    def __init__(self):
        self.file_summaries = []
        self.total_tokens = 0
        pass

    def load_template(self, template_path):
        template = yaml.safe_load(open(template_path))
        self.code_master = template["code_master_template"]
        self.readme_master = template["readme_master_template"]
        self.path = template['paths']

    def load_llm(self):
        self.code_master_llm = ChatGoogleGenerativeAI(**self.code_master['llm'])
        self.readme_master_llm = ChatGoogleGenerativeAI(**self.readme_master['llm'])
    
    def load_prompt(self):
        self.code_master_prompt = PromptTemplate(template=self.code_master['prompt'], input_variables=['file_content'])
        self.readme_master_prompt = PromptTemplate(template=self.readme_master['prompt'], input_variables=['summaries'])

    def create_filepaths(self) -> list[str]:
        filenames = []
        for i in self.path:
            if os.path.isdir(i):
                filenames.append(list_files_recursively_os_walk(i))
            else:
                filenames.append([i])
        filepaths = list(chain.from_iterable(filenames))
        return [i for i in filepaths if "__pycache__" not in i]

    def load_code_file(self, path: str) -> str:
        with open(path, "r") as f:
            content = f.read()
        return content

    def loop_over_files(self):
        filepaths = self.create_filepaths()
        for i in filepaths:
            if os.path.isdir(i):
                continue
            if i.endswith("md"):
                continue
            summary_chain = self.code_master_prompt | self.code_master_llm 
            file_code_content = self.load_code_file(i)
            if file_code_content == "":
                self.file_summaries.append({
                    "filename": i,
                    "summary": "the file is empty."
                })
                continue
            logger.info(f"calling LLM para {i}")
            summary = summary_chain.invoke(input=file_code_content)
            self.file_summaries.append({
                "filename": i,
                "summary": summary.content
            })
            self.total_tokens += summary.usage_metadata['total_tokens']

    def generate_readme(self):
        formatted_summaries = "\n\n".join(
        [f"File: {s['filename']}\nSummary: {s['summary']}" 
         for s in self.file_summaries])
        logger.info(f"calling LLM readme")
        readme_chain = self.readme_master_prompt | self.readme_master_llm
        final = readme_chain.invoke(input=formatted_summaries)
        now = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        with open(os.path.join(os.getcwd(), f"README_{now}.md"), "w") as readme_file:
            readme_file.write(final.content)
        with open(os.path.join(os.getcwd(), "file_summary"), "w") as summaries:
            for i in self.file_summaries:
                summaries.write(json.dumps(i) + "\n")
        self.total_tokens += final.usage_metadata['total_tokens']

def docgen_runner(template_path: str):
    logger.info("iniciando...")
    doc = DocGen()
    doc.load_template(template_path)
    doc.load_prompt()
    doc.load_llm()
    doc.create_filepaths()
    doc.loop_over_files()
    doc.generate_readme()
    logger.info(f"total tokens: {doc.total_tokens}")