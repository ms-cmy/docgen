# Gerador de doc automática

## Instalação

```shell
pip install git+https://github.com/ms-cmy/docgen 
```

para rodar, precisa das seguintes variáveis de ambiente:

```
GOOGLE_API_KEY=SUA_API_KEY
BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

limitações:
por enquanto só é possível utilizar modelos da **GOOGLE**.
por enquanto o nome dos agentes está fixo.

## Utilização

copie o yaml abaixo e modifique as partes

```yaml
paths: ['path1', 'arquivo_1.py', 'path/para/arquivo_2.py', 'path2']

code_master_template:
  prompt: >
          # Aqui fica o prompt que irá acessar cada arquivo
          # {file_content} é obrigatório, é onde vamos passar o que há no arquivo no prompt.
  llm:
    temperature: 0.2
    model: gemini-2.0-flash-lite

readme_master_template: 
  prompt: >
        # aqui é quem irá gerar o resumo, {summaries} é obrigatório, pois é onde receberá os resumos dos arquivos
  llm:
    temperature: 0
    model: gemini-2.0-flash-thinking-exp-01-21
```

depois de construir o yaml, é só rodar:

```shell
doc-gen -f example.yaml
```

[Exemplo de um doc gerado automaticamente](README_19_03_2025,14:24:29.md)

[com o seguinte yaml](example.yaml)


# Para o futuro

- utilizar langGraph para ficar mais costumizável o yaml (foi usado langchain inicialmente somente para teste)
- conseguir criar um prompt específico para uma pasta/arquivo/extensão de arquivo
- melhorar cli
- deixar readme em inglês