import psycopg2
from psycopg2 import sql

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="vectordb",
        user="admin",
        password="secret",
        port=5432
    )

def check_if_exists(function_name: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("""select function_name from documents where function_name = %s"""), (function_name, ))
            result = []
            for row in cur.fetchall():
                result.append(row)
        if result:
            return True
        return False

def insert_document(data: dict):
    """Insert a document with embedding"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("""
                    INSERT INTO documents (function_name, embedding, original_text, source_code)
                    VALUES (%s, %s, %s, %s)
                """),
                (
                    data['function_name'],
                    data['embed'],
                    data['text_that_got_embed'],
                    data['source_code']
                )
            )
        conn.commit()
        
def get_similarity(query_embedding: list[float], limit: int=3):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("""
                                SELECT 
                                function_name, 
                                original_text,
                                1 - (embedding <=> (%s)::vector) as similarity,
                                source_code
                                FROM documents
                                ORDER BY similarity DESC
                                LIMIT %s"""),
                (query_embedding, limit))
            results = []
            for row in cur.fetchall():
                results.append({
                    'function_name': row[0],
                    'original_text': row[1],
                    'similarity': round(float(row[2]), 4),
                    'source_code': row[3]
                })
    return results