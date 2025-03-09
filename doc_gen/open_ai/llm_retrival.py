from openai import OpenAI
import dotenv
import os

dotenv.load_dotenv()

client = OpenAI(
    api_key=os.environ['TOKEN'],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

def format_answer(answer: dict):
    values = []
    for en, (key, item) in enumerate(answer.items()):
        values.append({en: item[1]})
    return values

def generate_function_embedding(function: str, general_context=None):
    chat = client.chat.completions.create(
        model="gemini-2.0-flash-lite",
        messages=[{"role": "system", "content": """Create documentation text for the following code, given that: 
                                                    - Describe ONLY the core purpose and validation logic
                                                    - Use active voice without mentioning "function" or "this". Keep imperative voice.
                                                    - Start sentences with verbs
                                                    - Keep under 200 words
                                                    - Use noun phrases describing core operations
                                                    - Avoid pronouns and determiners (the, this)
                                                    - focus on the the minimum necessary underlying concepts (explaining the function itself) rather than the implementation itself"""},
                {"role": "user", "content": function}],
        temperature=0,
        max_tokens=400)
    return chat.choices[0].message.content

def get_embeddings_llm(query: str, answer: str = None):
    if answer:
        answer = format_answer(answer=answer)
    messages = [{"role": "system", "content": """You will rewrite the user question, it will be searched in a vector store.
                                                   Given the user question, transform it into the imperative mode, given that: 
                                                    - substitute anything that includes "function" or "this". Keep imperative voice.
                                                    - Start sentences with verbs
                                                    - Keep under 25 words
                                                    - Use noun phrases
                                                    - remove pronouns and determiners (the, this)
                                                    - focus on the minimum necessary to still be a good resume for what the user asked
                                                    - Do not use ponctuation marks only words and the final period."""},
                {"role": "user", "content": query},
                {"role": "system", "content": f"given this answers from the vector store, in no particular order are: {answer}, return to the user the one that mostly attend to his question."} if answer is not None else None]
    messages = list(filter(None, messages))
    chat = client.chat.completions.create(
        model="gemini-2.0-flash-lite",
        messages=messages,
        temperature=0,
        max_tokens=400)
    return chat.choices[0].message.content