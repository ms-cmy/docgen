# Projeto de geração de documentação


## 1o tentativa

A primeira tentativa na abordagem desse problema incluiu utilizar vector store, porém da seguinte forma:

Código sem doctring/documentação -> passa por uma LLM para gerar uma documentação extremamente resumida com palavras chave ->
envia para o postgrasql.

Na hora de recuperar algum código:

usuário escreve o query -> passa pela LLM -> vai para o vector store -> pesquisa as 5 top mais semelhantes -> volta para a LLM -> LLM escolhe a melhor para responder a pergunta do usuário (talvez não precise dessa última parte dependendo do usuário)


Como foi feito isso:

**Utilizando o meu computador local** eu levantei [essa api](api_endpoint_models/app.py) que carregava o modelo de embedding e fazia contato com a base [postgrasql](infra/postgresql/compose.yaml) que também foi levantada localemnte

Ponto 1: não utilizei cloud por questões de agilidade, e não vi a necessidade de ter custos para esse teste
Ponto 2: porque levantou uma api se estava tudo local? Honestamente, mais fácil de lidar com o que está acontecendo, consigo fazer requisições, ver falhas no código (flask levantado como debugger) e já ir resolvendo tudo de maneira interativa.

Alguns exemplos do fluxo acima ocorrendo:

```python
from doc_gen.custom_retrieval.model_retrieval import (publish_retrieval,
                                                      get_retrieval,
                                                      get_more_complex_retrival,
                                                      db_retrieval)
import dotenv
dotenv.load_dotenv()
import pprint

query_1 = """
    pub fn new_random(rows: usize, cols: usize) -> Mat {
        let size = rows * cols;
        let mut rng = rand::thread_rng();
        Mat {
            rows,
            cols,
            es: (0..size).map(|_| rng.r#gen::<f32>()).collect(),
        }
    }
"""

query_2 = """
    pub fn new_matrix(rows: usize, cols: usize, es: Vec<f32>) -> Mat {
        Mat::check_size(&rows, &cols, &es).unwrap_or_else(|err| panic!("matrix creation failed {:?}", err));
        Mat { rows, cols, es }
    }
"""

query_3 = """
    pub fn new_empty(rows: usize, cols: usize) -> Mat {
        let size = rows * cols;
        let es: Vec<f32> = vec![0.0; size];
        Mat { rows, cols, es }
    }
"""

query_4 = """
    pub fn new_identity(size: usize) -> Mat {
        let mut m = Mat::new_empty(size, size);
        for i in 0..size {
            m.set_at(i, i, 1.0);
        }
        m
    }
"""
for i, a in zip([query_1, query_2, query_3, query_4], ["new_random", "new_matrix", "new_empty", "new_identity"]):
    publish_retrieval(function_name=a, contents=i)
```

foi utilizado esse código em rust pois essas funções realizam algo extremamente semelhante: gerar matrix utilizando o struct (semelhante a classe em python) para criar uma matrix nova.

no terminal que está enviando as solicitações, podemos ver:

```shell
INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/openai/chat/completions "HTTP/1.1 200 OK"
```

na api:
```shell
2025-03-11 17:57:01 - Emb save no sql começou
2025-03-11 17:57:02 - send_to_banco ms response: 0.26
2025-03-11 17:57:02 - 192.168.0.106 - - [11/Mar/2025 17:57:02] "POST /to_bd HTTP/1.1" 200 -
2025-03-11 17:57:02 - Emb save no sql começou
2025-03-11 17:57:02 - send_to_banco ms response: 0.04, already exist, finishing early
2025-03-11 17:57:02 - 192.168.0.106 - - [11/Mar/2025 17:57:02] "POST /to_bd HTTP/1.1" 200 -
2025-03-11 17:57:03 - Emb save no sql começou
2025-03-11 17:57:03 - send_to_banco ms response: 0.04, already exist, finishing early
2025-03-11 17:57:03 - 192.168.0.106 - - [11/Mar/2025 17:57:03] "POST /to_bd HTTP/1.1" 200 -
2025-03-11 17:57:04 - Emb save no sql começou
2025-03-11 17:57:04 - send_to_banco ms response: 0.04, already exist, finishing early
2025-03-11 17:57:04 - 192.168.0.106 - - [11/Mar/2025 17:57:04] "POST /to_bd HTTP/1.1" 200 -
``` 
por um erro inicialmente enviei todas as funções com o mesmo nome, assim a api só reaproveita o que existe ao invés de criar diversos embeddings semelhantes, porém já é possível entender o que a api está devolvendo.

Agora, vamos recuperar os embeddings:

```python
>> print(get_more_complex_retrival("I need a function that creates a new matrix with random values"))
```

isso irá gerar:

```rust
pub fn new_random(rows: usize, cols: usize) -> Mat {
    let size = rows * cols;
    let mut rng = rand::thread_rng();
    Mat {
        rows,
        cols,
        es: (0..size).map(|_| rng.r#gen::<f32>()).collect(),
    }
}
```

podemos ver como é salvo na tabela do sql também (note que a coluna "original text" foi gerada pela LLM):

```python
pprint.pprint(db_retrieval("Create matrix", True))
[{'function_name': 'new_empty',
  'original_text': 'create matrix with specified dimensions. \n'
                   'calculate total number of elements using rows and '
                   'columns.\n'
                   'create vector of floating-point numbers, initializing all '
                   'elements to zero, based on calculated size.\n'
                   'construct matrix using provided dimensions and created '
                   'vector.\n'
                   'return new matrix.',
  'similarity': 0.7722,
  'source_code': '\n'
                 '    pub fn new_empty(rows: usize, cols: usize) -> Mat {\n'
                 '        let size = rows * cols;\n'
                 '        let es: Vec<f32> = vec![0.0; size];\n'
                 '        Mat { rows, cols, es }\n'
                 '    }\n'},
 {'function_name': 'new_identity',
  'original_text': 'create identity matrix. \n'
                   'allocate square matrix.\n'
                   'iterate through matrix diagonal.\n'
                   'set diagonal elements to one.\n'
                   'return identity matrix.',
  'similarity': 0.7262,
  'source_code': '\n'
                 '    pub fn new_identity(size: usize) -> Mat {\n'
                 '        let mut m = Mat::new_empty(size, size);\n'
                 '        for i in 0..size {\n'
                 '            m.set_at(i, i, 1.0);\n'
                 '        }\n'
                 '        m\n'
                 '    }\n'},
 {'function_name': 'new_random',
  'original_text': 'generate random matrix.\n'
                   '\n'
                   'accept matrix dimensions, rows and columns.\n'
                   'compute matrix size based on dimensions.\n'
                   'create random number generator.\n'
                   'generate matrix elements using random number generator.\n'
                   'collect generated elements into vector.\n'
                   'construct matrix using dimensions and element vector.\n'
                   'return constructed matrix.',
  'similarity': 0.6628,
  'source_code': '\n'
                 '    pub fn new_random(rows: usize, cols: usize) -> Mat {\n'
                 '        let size = rows * cols;\n'
                 '        let mut rng = rand::thread_rng();\n'
                 '        Mat {\n'
                 '            rows,\n'
                 '            cols,\n'
                 '            es: (0..size).map(|_| '
                 'rng.r#gen::<f32>()).collect(),\n'
                 '        }\n'
                 '    }\n'}]
```

## Analisando resultados:

porém, senti que essa abordagem estava dando muitas voltas, por exemplo, poderíamos utilizar a LLM para gerar as palavras chaves, e utilizar outra forma de busca mais simples para buscar em um banco, ou algo mais simples.

Além de que, o processo ficou relativamente manual, seria possível automatizar para um arquivo cada vez que fosse necessário, e para uma prova de conceito ficou meio rígido. Parece que isso serveria mais como suporte do que a solução em si.


# Segunda tentativa:

**Agentes**
Como gerar com facilidade um agente que lê o código e outro agente que faz a "junção de tudo"?

resposta: https://python.langchain.com/docs/introduction/

essa é a maneira mais fácil de gerar agentes.
Agora, para mostrar em uma apresentação de maneira simples preciso criar uma biblioteca python, somente para fazer entrada no CLI e realizar a criação dos documentos de maneira fácil.

Então, esse CLI irá precisar apontar para um template, é extremamente fácil utilizar templates com yaml, ainda mais em uma apresentação, todos poderão ver tudo que está sendo passado pela LLM, mais fácil de explicar o passo a passo e justificar o que está sendo feito.

Logo, parti para a criação da biblioteca que se encontra em: [Lib](doc_gen) (arquivos sem __init__.py NÃO entram na geração da biblioteca pelo jeito que está sendo feito pelo [setup.py](setup.py))

[o cli foi feito rapidamente utilizando click](doc_gen/cli/cli.py)

[com utilização de langchain](doc_gen/agent_doc_gen/long_agents.py) foi extremamente rápido produzir um MVP.

[um exemplo extremamente simples de yaml](example.yaml)

para a instalação:

```shell
pip install .
```

e utilização:

```shell
doc-gen -f example.yaml
```

exemplos de docs gerados sobre a documentação da primeira tentativa se encontram em: [Link](docs_gerados_sozinhos)


[a doc mais recente](docs_gerados_sozinhos/README_11_03_202518:24:43.md) está documentando a si própria (essa biblioteca que está gerando os readme.md!) [foi utilizado esse template](code_generation.yaml)


O requirements.txt contém mais bibliotecas do que o necessário, pois contém algumas da tentativa anterior, mas caso queiram testar é possível.

será necessária as seguintes variáveis de ambiente:

```txt (essa apikey eu peguei do https://aistudio.google.com/prompts/new_chat, não sei se funcionaria com a key default do gcloud auth etc)
GOOGLE_API_KEY=**
BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```
