# Code Embedding and Retrieval API

## 1. Project Overview

This project provides a Flask API for generating sentence embeddings, storing them, and retrieving semantically similar code snippets. It leverages pre-trained sentence transformer models to create embeddings and offers options for storing and retrieving data from both local JSONL files and a PostgreSQL database. This API is designed to facilitate code search and retrieval based on semantic similarity, enabling users to find relevant code snippets by querying with natural language phrases.

## 2. File Structure

```
.
├── app.py            # Defines the Flask API endpoints for embedding and retrieval.
├── db_connect.py     # Handles database connection and operations for PostgreSQL.
├── model_loader.py   # Loads the sentence transformer model and provides embedding functions.
├── requirements.txt  # Lists Python dependencies for the project.
└── __init__.py       # Initializes the project as a Python package.
```

- **`app.py`**:  This file is the core of the API. It sets up the Flask application and defines the following endpoints:
    - `/health`:  API health check.
    - `/rag`: Generates sentence embeddings for provided text.
    - `/emb_save`: Generates and saves embeddings along with function name and code to a local JSONL file.
    - `/retrive`: Retrieves similar code snippets from the local JSONL file based on a query phrase.
    - `/to_bd`: Saves embeddings, function name, and code to a PostgreSQL database, checking for duplicates.
    - `/retrive_from_banco`: Retrieves similar code snippets from the PostgreSQL database based on a query phrase.

- **`db_connect.py`**: This file manages the connection to the PostgreSQL database named "vectordb". It provides functions to:
    - Establish a database connection.
    - Check if a document (function) already exists in the database.
    - Insert new documents (function name, embedding, original text, source code) into the database.
    - Retrieve similar documents from the database based on embedding similarity to a query.

- **`model_loader.py`**: This file is responsible for loading the pre-trained sentence transformer model (`paraphrase-multilingual-MiniLM-L12-v2`). It includes functions to:
    - Load the sentence transformer model.
    - Encode sentences into embeddings using the loaded model.
    - Calculate cosine similarity between embeddings.

- **`requirements.txt`**: This file lists all the necessary Python packages required to run the Flask API, including Flask, sentence transformers, psycopg2 (for PostgreSQL), and potentially others.

- **`__init__.py`**: This file likely serves to initialize the project directory as a Python package, allowing for modular imports and organization.

## 3. Getting Started

To get started with this project, follow these steps:

1. **Prerequisites:**
    - Python 3.x
    - pip (Python package installer)
    - PostgreSQL database instance (named "vectordb" or configurable)

2. **Installation:**
    - Clone the repository to your local machine.
    - Navigate to the project directory in your terminal.
    - Create a virtual environment (recommended):
      ```bash
      python -m venv venv
      source venv/bin/activate  # On Linux/macOS
      venv\Scripts\activate  # On Windows
      ```
    - Install the required Python packages:
      ```bash
      pip install -r requirements.txt
      ```

3. **Database Setup (PostgreSQL):**
    - Ensure you have a PostgreSQL database instance running.
    - Create a database named "vectordb" if it doesn't exist.
    - Configure the database connection details (host, port, username, password, database name) within the `db_connect.py` file or environment variables as needed.

4. **Running the API:**
    - From the project directory, run the Flask application:
      ```bash
      flask run
      ```
    - The API will be accessible at the default Flask development server address (usually `http://127.0.0.1:5000/`).

## 4. Key Features

- **Sentence Embedding Generation:** Utilizes pre-trained sentence transformer models to generate high-quality embeddings for text input.
- **Local and Database Storage:** Supports saving embeddings and associated code snippets to both local JSONL files for simple setups and a PostgreSQL database for more robust and scalable storage.
- **Semantic Code Retrieval:** Enables retrieval of code snippets based on semantic similarity to a given query phrase, improving code search accuracy compared to keyword-based searches.
- **API Endpoints for Core Functionality:** Provides clear and well-defined API endpoints for health checks, embedding generation, saving embeddings, and retrieving similar code snippets from both local files and the database.
- **Database Integration:** Integrates with PostgreSQL for persistent and scalable storage of embeddings and metadata, including functionality to check for existing documents before insertion.
- **Logging:** Includes logging mechanisms for monitoring API usage and performance.