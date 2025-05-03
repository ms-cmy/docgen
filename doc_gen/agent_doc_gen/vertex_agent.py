# todo: needs to be generic between different models
# TODO: hd to change everything to use vertex ai should create a separated file to use vertex ai
from langchain_google_vertexai import VertexAI
from langchain.prompts import PromptTemplate
from itertools import chain
from typing import Union
import datetime
import yaml
import logging
import os
import json
import sys

FORMAT = '%(asctime)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

debug = os.environ.get("DEBUG_DOCGEN", False)

def list_files_recursively_os_walk(folder_path):
    file_list = []
    if not os.path.isdir(folder_path):
        raise Exception("xd")
    
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            file_list.append(full_path)
    return file_list

def from_ipynb_to_list(mb_target: str,
                     file: str = "main.py"):
    code = json.load(open(mb_target))
    py_file = []

    for cell in code['cells']:
        if cell['cell_type'] == 'code':
            for line in cell['source']:
                py_file.append(line)
        elif cell['cell_type'] == 'markdown':
            py_file.append("\n")
            for line in cell['source']:
                if line and line[0] == "#":
                    py_file.append(line)
            py_file.append("\n")
    return py_file
    

class DocGen:
    def __init__(self):
        self.file_summaries = []
        self.agents = {}
        # self.total_tokens = 0
        pass

    def parse_notebooks(self, path: str)-> list[str]:
        return from_ipynb_to_list(path)
    
    # transform the typehint into a class to share in other places
    def load_yaml(self, template_path: str) -> dict[str, Union[str, dict]]:
        template = yaml.safe_load(open(template_path))
        self.check_yaml(template)
        return template
    
    def check_yaml(self, template: dict[str, Union[str, dict]]):
        if template.get("paths") is None:
            raise Exception("template needs paths key to know where to look for files.")
        template_keys = template.keys()
        if any(i for i in template_keys if i.startswith("agent")) is False:
            # need to pass an example from github as error
            raise Exception("at least one agent needs to be created in the template.")

    def load_template(self, template_path):
        template = self.load_yaml(template_path)
        for key, value in template.items():
            if key.startswith("agent"):
                self.agents[key] = {"template": value, "llm": self.load_agent(value)}
        self.path = template['paths']
        self.exclude_extensions = tuple(template.get("ignore_extensions", None))
    
    def create_node_run(self) -> list[tuple]:
        """
        tuple's output:
        (agent_name, input, output)
        """
        input_output = []
        for key, value in self.agents.items():
            input_output.append((key, value[0].get("input", None), value[0].get("output", None)))
        xd = self.node_looper(input_output)
        return xd

    # write tests for this
    # ive got zero clue why it is working correctly.
    def node_looper(self, input_nodes: list[tuple]):
        order_to_run = {None: 0}
        list_order_to_run = []
        while len(list_order_to_run) != len(input_nodes):
            for i in input_nodes:
                for key, value in order_to_run.items():
                    if i[1] == key:
                        list_order_to_run.append((*i, value))
                        if i[2] not in order_to_run.keys():
                            order_to_run[i[2]] = value + 1
                            break
        return list_order_to_run

    def load_agent(self, agent_template: dict):
        """
        order: prompt | LLM
        deal if llm is empty
        """
        return PromptTemplate(template=agent_template['prompt'],
                              input_variables=agent_template.get('input', 'file_content')) | VertexAI(**agent_template['llm'])

    def exclude_paths(self, filepaths: list[str]) -> list[str]:
        return [i for i in filepaths if not i.endswith(self.exclude_extensions)]

    def create_filepaths(self) -> list[str]:
        filenames = []
        for i in self.path:
            if os.path.isdir(i):
                filenames.append(list_files_recursively_os_walk(i))
            else:
                filenames.append([i])
        filepaths = list(chain.from_iterable(filenames))
        filepaths = self.exclude_paths(filepaths)
        return [i for i in filepaths if "__pycache__" not in i]

    def load_code_file(self, path: str) -> str:
        # if/elif for different file formats that require some working
        if path.endswith("ipynb"):
            content = self.parse_notebooks(path)
        else:
            with open(path, "r") as f:
                content = f.read()
        return content
    
    def is_file_empty(self, file_content: str) -> bool:
        if file_content == "":
            return True
        return False
    
    def agents_to_read_file(self, filepaths):
        run = {}
        xd = {}
        for key, value in self.agents.items():
            extensions = value[0].get('extensions')
            extensions = extensions if isinstance(extensions, list) else [extensions]
            for i in extensions:
                xd[i] = key
        for i in filepaths:
            run[i] = xd.get(i.split(".")[-1])
        return run    
    
    def loop_over_files(self):
        filepaths = self.create_filepaths()
        run_order = self.create_node_run()
        out = self.agents_to_read_file(filepaths)
        results = {}
        # for i in filepaths:
        #     file_code_content = self.load_code_file(i)
        #     if self.is_file_empty(i):
        #         self.file_summaries.append({
        #             "filename": i,
        #             "summary": "the file is empty."})
        for file_path, agent in out.items():
            file_content = self.load_code_file(file_path)
            summary = self.agents.get(agent).get("llm").invoke(input=file_content)
            
            # logger.info(f"calling LLM for file: {i} for agent {agent}")
            # self.file_summaries.append({
            #     'filename': i,
            #     'agent': 
            # })
            
            


    # def loop_over_files(self):
    #     filepaths = self.create_filepaths()
    #     for i in filepaths:
    #         if os.path.isdir(i):
    #             continue
    #         if i.endswith("md"):
    #             continue
    #         summary_chain = self.code_master_prompt | self.code_master_llm 
    #         file_code_content = self.load_code_file(i)
    #         if file_code_content == "":
    #             self.file_summaries.append({
    #                 "filename": i,
    #                 "summary": "the file is empty."
    #             })
    #             continue
    #         logger.info(f"calling LLM para {i}")
    #         summary = summary_chain.invoke(input=file_code_content)
    #         self.file_summaries.append({
    #             "filename": i,
    #             "summary": summary
    #         })
            # self.total_tokens += summary.usage_metadata['total_tokens']
    
    # TODO: XD?
    def remove_markdown_notation(self, text: str) -> str:
        return text[11:-3]

    def generate_readme(self):
        formatted_summaries = "\n\n".join(
        [f"File: {s['filename']}\nSummary: {s['summary']}" 
         for s in self.file_summaries])
        logger.info(f"calling LLM readme")
        readme_chain = self.readme_master_prompt | self.readme_master_llm
        final = readme_chain.invoke(input=formatted_summaries)
        now = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        final = self.remove_markdown_notation(final)
        # change this urgently
        if sys.platform.startswith("linux"):
            with open(os.path.join(os.getcwd(), f"README_{now}.md"), "w") as readme_file:
                readme_file.write(final)
        else:
            with open(os.path.join(os.getcwd(), f"README_{now}.md"), "w", encoding="utf-8") as readme_file:
                readme_file.write(final)
        if debug:
            with open(os.path.join(os.getcwd(), "file_summary"), "w") as summaries:
                for i in self.file_summaries:
                    summaries.write(json.dumps(i) + "\n")
        # self.total_tokens += final.usage_metadata['total_tokens']

def docgen_runner(template_path: str):
    logger.info("iniciando...")
    doc = DocGen()
    doc.load_template(template_path)
    doc.create_filepaths()
    doc.loop_over_files()
    doc.generate_readme()